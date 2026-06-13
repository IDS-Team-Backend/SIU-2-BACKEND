#!/usr/bin/env bash
# Refresh completo de la DB: dropea, recrea el schema y resiembra.
# Uso: bash refresh_db.sh   (o: chmod +x refresh_db.sh && ./refresh_db.sh)
# Para usar un venv: PYTHON=./venv/bin/python ./refresh_db.sh
set -euo pipefail

# init_db.py y seed.py usan rutas relativas (schema.sql, imports), así que hay
# que pararse en el directorio del backend antes de ejecutarlos.
cd "$(dirname "$0")/SIU-2-BACKEND"

PYTHON="${PYTHON:-python3}"

echo "==> Reinicializando la base (init_db.py)..."
"$PYTHON" init_db.py

echo "==> Sembrando datos (seed.py)..."
"$PYTHON" seed.py

echo "==> Refresh completo."
