"""API REST de alarmas (Flask). El frontend vive aparte y solo consume estos endpoints."""
from datetime import datetime

from flask import Flask, jsonify, request, send_file

import alarmas_service
import config
import db
import exporter
import resumen
from parsing import parse_csv

MAX_BYTES = 10 * 1024 * 1024


def ahora_colombia() -> datetime:
    """Hora actual de Colombia, sin zona (las fechas del CSV vienen en hora local)."""
    return datetime.now(config.TZ).replace(tzinfo=None, microsecond=0)


def create_app(db_path: str | None = None, reloj=ahora_colombia) -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_BYTES
    path = db_path or config.DB_PATH

    def con():
        return db.conectar(path)

    @app.after_request
    def cors(resp):
        resp.headers["Access-Control-Allow-Origin"] = config.CORS_ORIGIN
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
        resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return resp

    def error(msg, code):
        return jsonify({"error": msg}), code

    @app.errorhandler(413)
    def demasiado_grande(_):
        return error("El archivo supera el máximo de 10 MB", 413)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "ahora": reloj().isoformat()}

    @app.post("/api/alarmas/importar")
    def importar():
        archivo = request.files.get("archivo")
        if archivo is None or not archivo.filename:
            return error("Envía el CSV en el campo 'archivo' (multipart/form-data)", 400)
        try:
            alarmas, errores = parse_csv(archivo.read())
        except ValueError as e:
            return error(str(e), 400)
        c = con()
        try:
            resultado = db.guardar_alarmas(c, alarmas)
        finally:
            c.close()
        return jsonify({**resultado, "rechazadas": len(errores), "errores": errores[:20]}), 201

    def _listar():
        filtro = request.args.get("nivel", "todos").lower()
        c = con()
        try:
            return alarmas_service.listar(db.leer_alarmas(c), reloj(), filtro)
        finally:
            c.close()

    @app.get("/api/alarmas")
    def listar():
        try:
            registros, conteos = _listar()
        except ValueError as e:
            return error(str(e), 400)
        return jsonify({"conteos": conteos, "total": len(registros), "alarmas": registros})

    @app.get("/api/alarmas/exportar")
    def exportar():
        try:
            registros, _ = _listar()
        except ValueError as e:
            return error(str(e), 400)
        nombre = f"alarmas_{request.args.get('nivel', 'todos').lower()}_{reloj():%Y%m%d_%H%M%S}.xlsx"
        return send_file(exporter.a_excel(registros), as_attachment=True, download_name=nombre,
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    @app.delete("/api/alarmas")
    def borrar():
        c = con()
        try:
            return {"eliminadas": db.borrar_todo(c)}
        finally:
            c.close()

    @app.get("/api/resumen")
    def resumen_dia():
        c = con()
        try:
            alarmas = db.leer_alarmas(c)
        finally:
            c.close()
        try:
            return jsonify(resumen.construir_resumen(alarmas, reloj()))
        except NotImplementedError as e:
            return error(str(e), 501)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=True)
