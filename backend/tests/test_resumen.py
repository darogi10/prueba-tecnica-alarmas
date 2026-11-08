"""Contrato del servicio de resumen. (sin IA)."""
from datetime import datetime
from parsing import Alarma
from resumen import construir_resumen

AHORA = datetime(2026, 11, 5, 14, 0, 0)


def alarma(i, fecha):
    return Alarma(i, 0, 0, 100, fecha, "X", "Y", "N")


def test_solo_cuenta_hoy():
    alarmas = [alarma(1, datetime(2026, 11, 5, 8, 10)), alarma(2, datetime(2026, 11, 4, 8, 10))]
    r = construir_resumen(alarmas, AHORA)
    assert r["fecha"] == "2026-11-05" and r["total"] == 1


def test_agrupa_por_hora():
    alarmas = [alarma(1, datetime(2026, 11, 5, 8, 10)), alarma(2, datetime(2026, 11, 5, 8, 59)), alarma(3, datetime(2026, 11, 5, 9, 0))]
    r = construir_resumen(alarmas, AHORA)
    por_hora = {x["hora"]: x["total"] for x in r["por_hora"]}
    assert por_hora["08:00"] == 2 and por_hora["09:00"] == 1


def test_sin_alarmas_hoy():
    r = construir_resumen([], AHORA)
    assert r["total"] == 0
