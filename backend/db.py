"""Persistencia en SQLite (sin ORM, para mantenerlo simple)."""
import sqlite3
from datetime import datetime

from parsing import Alarma

_SCHEMA = """
CREATE TABLE IF NOT EXISTS alarmas (
    id_alarma      INTEGER PRIMARY KEY,
    g2             INTEGER NOT NULL,
    g3             INTEGER NOT NULL,
    g4             INTEGER NOT NULL,
    fecha_creacion TEXT    NOT NULL,   -- ISO 8601, hora local
    municipio      TEXT    NOT NULL,
    departamento   TEXT    NOT NULL,
    notificada     TEXT    NOT NULL CHECK (notificada IN ('S','N'))
)
"""


def conectar(path: str) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute(_SCHEMA)
    return con


def guardar_alarmas(con: sqlite3.Connection, alarmas: list[Alarma]) -> dict:
    """Upsert por ID_ALARMA: reimportar el mismo archivo no duplica registros."""
    existentes = {r[0] for r in con.execute("SELECT id_alarma FROM alarmas")}
    nuevas = actualizadas = 0
    with con:
        for a in alarmas:
            if a.id_alarma in existentes:
                actualizadas += 1
            else:
                nuevas += 1
                existentes.add(a.id_alarma)
            con.execute(
                """INSERT INTO alarmas VALUES (?,?,?,?,?,?,?,?)
                   ON CONFLICT(id_alarma) DO UPDATE SET
                     g2=excluded.g2, g3=excluded.g3, g4=excluded.g4,
                     fecha_creacion=excluded.fecha_creacion, municipio=excluded.municipio,
                     departamento=excluded.departamento, notificada=excluded.notificada""",
                (a.id_alarma, a.g2, a.g3, a.g4, a.fecha_creacion.isoformat(),
                 a.municipio, a.departamento, a.notificada))
    return {"nuevas": nuevas, "actualizadas": actualizadas}


def leer_alarmas(con: sqlite3.Connection) -> list[Alarma]:
    filas = con.execute("SELECT * FROM alarmas ORDER BY fecha_creacion DESC, id_alarma DESC")
    return [Alarma(r["id_alarma"], r["g2"], r["g3"], r["g4"],
                   datetime.fromisoformat(r["fecha_creacion"]),
                   r["municipio"], r["departamento"], r["notificada"]) for r in filas]


def borrar_todo(con: sqlite3.Connection) -> int:
    with con:
        return con.execute("DELETE FROM alarmas").rowcount
