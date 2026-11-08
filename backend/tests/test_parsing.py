from datetime import datetime
import pytest
from parsing import parse_fecha, parse_csv


@pytest.mark.parametrize("txt,esperado", [
    ("09-OCT-26 10.12.56.000000000 PM", datetime(2026, 10, 9, 22, 12, 56)),
    ("10-OCT-26 07.45.56.000000000 AM", datetime(2026, 10, 10, 7, 45, 56)),
    ("04-NOV-26 12.05.00.000000000 AM", datetime(2026, 11, 4, 0, 5, 0)),   # 12 AM = medianoche
    ("04-NOV-26 12.05.00.000000000 PM", datetime(2026, 11, 4, 12, 5, 0)),  # 12 PM = mediodía
])
def test_parse_fecha(txt, esperado):
    assert parse_fecha(txt) == esperado


def test_fecha_invalida():
    with pytest.raises(ValueError):
        parse_fecha("2026-10-09 10:12:56")


def test_csv_con_filas_malas_no_tumba_todo():
    csv = ('"ID_ALARMA"|"2G"|"3G"|"4G"|"FECHA_CREACION"|"MUNICIPIO"|"DEPARTAMENTO"|"NOTIFICADA"\r\n'
           '1|0|0|13|09-OCT-26 10.12.56.000000000 PM|"Cabuyaro"|"Meta"|"N"\r\n'
           'x|0|0|13|09-OCT-26 10.12.56.000000000 PM|"Cabuyaro"|"Meta"|"N"\r\n'
           '3|0|0|13|fecha mala|"Cabuyaro"|"Meta"|"N"\r\n').encode()
    ok, errores = parse_csv(csv)
    assert [a.id_alarma for a in ok] == [1]
    assert [e["linea"] for e in errores] == [3, 4]


def test_encabezado_incorrecto():
    with pytest.raises(ValueError):
        parse_csv(b"a|b|c\r\n1|2|3\r\n")
