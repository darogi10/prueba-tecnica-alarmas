# Monitor de alarmas — Prueba técnica

Backend REST (Python/Flask + SQLite) y frontend (HTML/JS puro) **completamente desacoplados**:
el frontend solo habla con la API por `fetch`.

## Cómo correrlo
```bash
# Backend (puerto 5000)
cd backend
pip install -r requirements.txt
python app.py

# Frontend (otra terminal, puerto 5500)
cd frontend
python -m http.server 5500      # abrir http://localhost:5500
```
Luego pulsa **Importar CSV** y elige `datos/Muestra_de_datos.csv`.
Si cambias el puerto/host del backend, edita `frontend/config.js`.

Tests: `cd backend && pytest`

## API
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/alarmas/importar` | CSV `|` en el campo `archivo` (multipart). Upsert por `ID_ALARMA`; filas inválidas se reportan sin tumbar la importación |
| GET | `/api/alarmas?nivel=todos\|warn\|critico\|normal` | Alarmas con `duracion`, `duracion_segundos` y `nivel`, más `conteos` |
| GET | `/api/alarmas/exportar?nivel=...` | Excel con exactamente lo que muestra la tabla con ese filtro |
| GET | `/api/resumen` | Alarmas de hoy agrupadas por hora |
| DELETE | `/api/alarmas` | Limpia los datos |

## Reglas de negocio (`backend/classification.py`)
- Tecnología **disponible** = valor `>= 0` (el `-100` del CSV significa no disponible).
- Cumple la base si hay al menos una disponible, **todas las disponibles valen 100** y `NOTIFICADA = 'N'`.
- Duración = ahora (hora de Colombia) − `FECHA_CREACION`. `> 1h y <= 24h` → WARN; `> 24h` → CRÍTICO; si no → normal.

Decisiones: si ninguna tecnología está disponible no se marca (nada "al límite"); fechas futuras cuentan como duración 0;
la hora del CSV (`09-OCT-26 10.12.56.000000000 PM`) se interpreta como hora local de Colombia y se parsea sin depender del locale.