"""Servicios de listado: enriquecen las alarmas con duración y nivel."""
from datetime import datetime

from classification import NORMAL, WARN, CRITICO, clasificar, duracion, formatear_duracion
from parsing import Alarma

FILTROS = {"todos": None, "warn": WARN, "critico": CRITICO, "normal": NORMAL}


def enriquecer(a: Alarma, ahora: datetime) -> dict:
    d = duracion(a.fecha_creacion, ahora)
    return {
        "id_alarma": a.id_alarma,
        "g2": a.g2, "g3": a.g3, "g4": a.g4,
        "fecha_creacion": a.fecha_creacion.isoformat(),
        "municipio": a.municipio,
        "departamento": a.departamento,
        "notificada": a.notificada,
        "duracion_segundos": int(d.total_seconds()),
        "duracion": formatear_duracion(d),
        "nivel": clasificar(a.g2, a.g3, a.g4, a.notificada, a.fecha_creacion, ahora),
    }


def listar(alarmas: list[Alarma], ahora: datetime, filtro: str = "todos") -> tuple[list[dict], dict]:
    """Devuelve (registros filtrados, conteos por nivel sobre el total)."""
    if filtro not in FILTROS:
        raise ValueError(f"filtro inválido: {filtro!r}. Use: {', '.join(FILTROS)}")
    todos = [enriquecer(a, ahora) for a in alarmas]
    conteos = {"todos": len(todos)}
    for clave, nivel in FILTROS.items():
        if nivel:
            conteos[clave] = sum(1 for r in todos if r["nivel"] == nivel)
    nivel = FILTROS[filtro]
    return ([r for r in todos if nivel is None or r["nivel"] == nivel], conteos)
