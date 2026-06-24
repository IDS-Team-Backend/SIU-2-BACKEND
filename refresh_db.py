#!/usr/bin/env python3
"""Refresh completo de la DB: dropea, recrea el schema y resiembra.

Pensado para correr dentro del contenedor `api` (donde el backend está en /app):
    docker compose exec api python refresh_db.py
Se para en el directorio del backend (donde viven init_db.py / seed.py / schema.sql),
así que funciona sin importar el CWD.
"""
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)

import init_db
import seed


def main():
    print("==> Reinicializando la base (init_db.py)...")
    init_db.init_database()

    print("==> Sembrando datos (seed.py)...")
    seed.run_seed()

    print("==> Refresh completo.")


if __name__ == "__main__":
    main()
