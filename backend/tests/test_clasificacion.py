from datetime import datetime, timedelta
import pytest
from classification import clasificar, cumple_condiciones_base, NORMAL, WARN, CRITICO

AHORA = datetime(2026, 11, 5, 14, 0, 0)


def nivel(g2=-100, g3=-100, g4=100, notif="N", hace=timedelta(hours=2)):
    return clasificar(g2, g3, g4, notif, AHORA - hace, AHORA)


def test_limites_de_tiempo():
    assert nivel(hace=timedelta(hours=1)) == NORMAL                       # exactamente 1h: no es > 1h
    assert nivel(hace=timedelta(hours=1, seconds=1)) == WARN
    assert nivel(hace=timedelta(hours=24)) == WARN                        # exactamente 24h: aún WARN
    assert nivel(hace=timedelta(hours=24, seconds=1)) == CRITICO


def test_solo_tecnologias_disponibles_cuentan():
    assert cumple_condiciones_base(100, -100, 100, "N")      # 3G no disponible, el resto en 100
    assert cumple_condiciones_base(100, 100, 100, "N")
    assert not cumple_condiciones_base(33, -100, 0, "N")
    assert not cumple_condiciones_base(0, 0, 100, "N")        # 0 está disponible y no es 100
    assert not cumple_condiciones_base(-100, -100, -100, "N")  # nada disponible


def test_notificada_s_nunca_es_alerta():
    assert nivel(notif="S", hace=timedelta(days=5)) == NORMAL


def test_condicion_base_no_cumplida_es_normal_aunque_sea_antigua():
    assert nivel(g2=50, g3=100, g4=100, hace=timedelta(days=5)) == NORMAL


def test_fecha_futura_es_normal():
    assert nivel(hace=timedelta(hours=-3)) == NORMAL
