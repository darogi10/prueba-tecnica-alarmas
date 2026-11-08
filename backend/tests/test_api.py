import io, os
from datetime import datetime
import pytest
from app import create_app

CSV = os.path.join(os.path.dirname(__file__), "..", "..", "datos", "Muestra_de_datos.csv")
AHORA = datetime(2026, 11, 5, 14, 0, 0)


@pytest.fixture
def client(tmp_path):
    return create_app(str(tmp_path / "t.db"), reloj=lambda: AHORA).test_client()


def importar(client):
    with open(CSV, "rb") as f:
        return client.post("/api/alarmas/importar", data={"archivo": (f, "m.csv")},
                           content_type="multipart/form-data")


def test_importar_y_reimportar_no_duplica(client):
    r = importar(client)
    assert r.status_code == 201 and r.json["nuevas"] == 1499 and r.json["rechazadas"] == 0
    r = importar(client)
    assert r.json["nuevas"] == 0 and r.json["actualizadas"] == 1499
    assert client.get("/api/alarmas").json["total"] == 1499


def test_filtros_son_consistentes(client):
    importar(client)
    d = client.get("/api/alarmas").json
    c = d["conteos"]
    assert c["warn"] + c["critico"] + c["normal"] == c["todos"]
    for f in ("warn", "critico", "normal"):
        d = client.get(f"/api/alarmas?nivel={f}").json
        assert d["total"] == c[f]
        assert all(a["nivel"] == f.upper() for a in d["alarmas"])
    assert c["critico"] > 0 and c["warn"] > 0


def test_critico_cumple_reglas(client):
    importar(client)
    for a in client.get("/api/alarmas?nivel=critico").json["alarmas"]:
        assert a["notificada"] == "N" and a["duracion_segundos"] > 86400
        assert all(t == 100 for t in (a["g2"], a["g3"], a["g4"]) if t >= 0)


def test_filtro_invalido(client):
    assert client.get("/api/alarmas?nivel=xxx").status_code == 400


def test_exportar_respeta_filtro(client):
    from openpyxl import load_workbook
    importar(client)
    n = client.get("/api/alarmas?nivel=warn").json["total"]
    r = client.get("/api/alarmas/exportar?nivel=warn")
    assert r.status_code == 200
    ws = load_workbook(io.BytesIO(r.data)).active
    assert ws.max_row - 1 == n
    assert {ws.cell(row=i, column=10).value for i in range(2, ws.max_row + 1)} == {"WARN"}


def test_importar_sin_archivo(client):
    assert client.post("/api/alarmas/importar").status_code == 400
