"""Configuración del backend."""
import os
from zoneinfo import ZoneInfo

DB_PATH = os.environ.get("ALARMAS_DB", os.path.join(os.path.dirname(__file__), "alarmas.db"))
TZ = ZoneInfo(os.environ.get("ALARMAS_TZ", "America/Bogota"))
# Origen permitido para CORS (el frontend corre en otro puerto/origen).
CORS_ORIGIN = os.environ.get("ALARMAS_CORS_ORIGIN", "*")
