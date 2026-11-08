"""Regla de negocio: categorización de alarmas por criticidad (función pura, sin BD)."""
from datetime import datetime, timedelta

NORMAL, WARN, CRITICO = "NORMAL", "WARN", "CRITICO"

UMBRAL_WARN = timedelta(hours=1)
UMBRAL_CRITICO = timedelta(hours=24)


def cumple_condiciones_base(g2: int, g3: int, g4: int, notificada: str) -> bool:
    """Las tres condiciones base de la prueba:

    1. Disponibilidad: una tecnología está disponible si su valor es >= 0 (-100 = no disponible).
    2. Capacidad al límite: TODAS las tecnologías disponibles valen exactamente 100.
       Si ninguna está disponible, no hay nada "al límite", así que no cumple.
    3. Notificación negativa: NOTIFICADA = 'N'.
    """
    disponibles = [t for t in (g2, g3, g4) if t >= 0]
    return bool(disponibles) and all(t == 100 for t in disponibles) and notificada == "N"


def duracion(fecha_creacion: datetime, ahora: datetime) -> timedelta:
    """Tiempo transcurrido desde la creación. Nunca negativo (fechas futuras -> 0)."""
    return max(ahora - fecha_creacion, timedelta(0))


def clasificar(g2: int, g3: int, g4: int, notificada: str,
               fecha_creacion: datetime, ahora: datetime) -> str:
    if not cumple_condiciones_base(g2, g3, g4, notificada):
        return NORMAL
    d = duracion(fecha_creacion, ahora)
    if d > UMBRAL_CRITICO:   # estrictamente > 24 h
        return CRITICO
    if d > UMBRAL_WARN:      # > 1 h y <= 24 h
        return WARN
    return NORMAL


def formatear_duracion(d: timedelta) -> str:
    total = int(d.total_seconds())
    dias, resto = divmod(total, 86400)
    horas, resto = divmod(resto, 3600)
    minutos = resto // 60
    if dias:
        return f"{dias}d {horas:02d}h {minutos:02d}m"
    return f"{horas:02d}h {minutos:02d}m"
