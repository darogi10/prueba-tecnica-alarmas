"""Exportación a Excel de lo que se ve en la tabla."""
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

_COLORES = {"WARN": "FFF3C4", "CRITICO": "F9C9C9"}
_ENCABEZADOS = ["ID_ALARMA", "2G", "3G", "4G", "FECHA_CREACION", "MUNICIPIO",
                "DEPARTAMENTO", "NOTIFICADA", "DURACION", "NIVEL"]


def a_excel(registros: list[dict]) -> BytesIO:
    from datetime import datetime
    wb = Workbook()
    ws = wb.active
    ws.title = "Alarmas"
    ws.append(_ENCABEZADOS)
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in registros:
        ws.append([r["id_alarma"], r["g2"], r["g3"], r["g4"],
                   datetime.fromisoformat(r["fecha_creacion"]), r["municipio"],
                   r["departamento"], r["notificada"], r["duracion"], r["nivel"]])
        ws.cell(row=ws.max_row, column=5).number_format = "yyyy-mm-dd hh:mm:ss"
        color = _COLORES.get(r["nivel"])
        if color:
            for c in ws[ws.max_row]:
                c.fill = PatternFill("solid", fgColor=color)
    for i, ancho in enumerate([12, 6, 6, 6, 20, 26, 20, 12, 14, 10], start=1):
        ws.column_dimensions[get_column_letter(i)].width = ancho
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
