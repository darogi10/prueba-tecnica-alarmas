"""Lectura y validación del CSV de alarmas (separado por '|')."""
import csv
import io
import re
from dataclasses import dataclass
from datetime import datetime

COLUMNAS = ["ID_ALARMA", "2G", "3G", "4G", "FECHA_CREACION", "MUNICIPIO", "DEPARTAMENTO", "NOTIFICADA"]

_MESES = {m: i for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], start=1)}
# Formato Oracle: 09-OCT-26 10.12.56.000000000 PM
_FECHA_RE = re.compile(r"^(\d{2})-([A-Za-z]{3})-(\d{2}) (\d{1,2})\.(\d{2})\.(\d{2})(?:\.\d{1,9})? (AM|PM)$")


@dataclass
class Alarma:
    id_alarma: int
    g2: int
    g3: int
    g4: int
    fecha_creacion: datetime  # hora local, sin zona (naive)
    municipio: str
    departamento: str
    notificada: str  # 'S' | 'N'


def parse_fecha(texto: str) -> datetime:
    """Convierte '09-OCT-26 10.12.56.000000000 PM' en datetime (sin depender del locale)."""
    m = _FECHA_RE.match(texto.strip())
    if not m:
        raise ValueError(f"fecha con formato inválido: {texto!r}")
    dia, mes, anio, hora, minuto, seg, ampm = m.groups()
    mes_num = _MESES.get(mes.upper())
    if mes_num is None:
        raise ValueError(f"mes desconocido: {mes!r}")
    hora = int(hora)
    if not 1 <= hora <= 12:
        raise ValueError(f"hora fuera de rango: {hora}")
    hora = hora % 12 + (12 if ampm == "PM" else 0)
    return datetime(2000 + int(anio), mes_num, int(dia), hora, int(minuto), int(seg))


def parse_csv(contenido: bytes) -> tuple[list[Alarma], list[dict]]:
    """Devuelve (alarmas válidas, errores). Una fila mala no tumba toda la importación.

    Lanza ValueError si el archivo no es un CSV de alarmas (encabezado incorrecto).
    """
    try:
        texto = contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = contenido.decode("latin-1")

    lector = csv.reader(io.StringIO(texto, newline=""), delimiter="|", quotechar='"')
    try:
        encabezado = [c.strip().upper() for c in next(lector)]
    except StopIteration:
        raise ValueError("El archivo está vacío")
    if encabezado != COLUMNAS:
        raise ValueError(f"Encabezado inválido. Se esperaba: {'|'.join(COLUMNAS)}")

    alarmas, errores = [], []
    for fila in lector:
        linea = lector.line_num
        if not fila:
            continue
        try:
            if len(fila) != len(COLUMNAS):
                raise ValueError(f"se esperaban {len(COLUMNAS)} columnas y llegaron {len(fila)}")
            notificada = fila[7].strip().upper()
            if notificada not in ("S", "N"):
                raise ValueError(f"NOTIFICADA debe ser S o N, llegó {fila[7]!r}")
            alarmas.append(Alarma(
                id_alarma=int(fila[0]),
                g2=int(fila[1]), g3=int(fila[2]), g4=int(fila[3]),
                fecha_creacion=parse_fecha(fila[4]),
                municipio=fila[5].strip(),
                departamento=fila[6].strip(),
                notificada=notificada,
            ))
        except ValueError as e:
            errores.append({"linea": linea, "error": str(e)})
    return alarmas, errores
