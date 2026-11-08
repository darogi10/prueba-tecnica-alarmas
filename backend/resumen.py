"""Servicio de RESUMEN DEL DÍA  ->  GET /api/resumen"""

from datetime import datetime
from parsing import Alarma


def construir_resumen(alarmas: list[Alarma], ahora: datetime) -> dict:

  # 1. Fecha de hoy
  hoy = ahora.date()

  # 2. Alarmas creadas hoy
  alarmas_hoy = []
  for alarma in alarmas:
    if alarma.fecha_creacion.date() == hoy:
      alarmas_hoy.append(alarma)

  # 3. Número de alarmas por hora
  conteo = {}
  for alarma in alarmas_hoy:
    hora = alarma.fecha_creacion.hour
    conteo[hora] = conteo.get(hora, 0) + 1

  # 4. Lista ordenada de diccionarios
  por_hora = []
  for hora in sorted(conteo):
    por_hora.append({"hora": f"{hora:02d}:00", "total": conteo[hora]})

  # 5. Fecha y total
  return {
    "fecha": hoy.isoformat(),
    "total": len(alarmas_hoy),
    "por_hora": por_hora,
  }