"""Setup global de los tests E2E.

Este archivo orquesta el entorno de testing y expone las **fixtures**
de pytest. La lógica pesada está en los módulos auxiliares:

- ``_db_stub``: schema SQLite + reemplazo de ``db.execute_query``.
- ``_factories``: helpers para crear usuarios, materias, cursos, etc.
- ``_auth_helpers``: ``login_como`` + parche del ``validar_token``.

Orden de booteo importante
==========================
La secuencia siguiente es crítica y por eso es lineal y no envuelta
en una función:

1. Setear env vars (JWT_SECRET, DB_*) antes de que cualquier módulo
   del backend lea ``os.getenv``.
2. Agregar ``backend/`` al ``sys.path`` para que los ``import db``,
   ``import services.*``, etc. funcionen tal cual están en producción.
3. Reemplazar ``db.execute_query`` por la versión SQLite **antes** de
   importar la app, porque al importar routers se cargan repositorios
   que ya lo usan.
4. Parchear ``utils.auth_validator.validar_token`` **antes** de
   importar la app, porque ``register_routes`` captura la referencia.
5. Importar la app (con todo lo anterior ya en su lugar).

Por qué los fixtures usan ``yield``
===================================
Un fixture de pytest se escribe como una función normal, pero si
necesita ejecutar código **después** del test (cleanup), usa ``yield``
en vez de ``return``. Todo lo que está antes del ``yield`` corre como
*setup* (antes del test); el valor que se entrega con ``yield`` es lo
que recibe el test como argumento; todo lo que está después del
``yield`` corre como *teardown* (después del test, incluso si falló).

Ejemplo:

    @pytest.fixture
    def client():
        with flask_app.test_client() as c:   # setup
            yield c                          # el test recibe `c`
        # acá iría el teardown si hiciera falta

Sin el ``yield``, no se podría ejecutar el ``__exit__`` del context
manager después del test. Por eso pytest fomenta este patrón.
"""

import os
import sys
from pathlib import Path

import pytest


# ─── 1. Env vars ─────────────────────────────────────────────────────────
#
# Los módulos del backend leen estas variables al importarse. Las
# seteamos antes de cualquier import para evitar errores y para que
# JWT_handler use una clave conocida.

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest-must-be-at-least-32-bytes")
os.environ.setdefault("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "2")
os.environ.setdefault("DB_HOST", "stub")
os.environ.setdefault("DB_USER", "stub")
os.environ.setdefault("DB_PASSWORD", "stub")
os.environ.setdefault("DB_NAME", "stub")
os.environ.setdefault("DB_PORT", "3306")


# ─── 2. sys.path ─────────────────────────────────────────────────────────

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ─── 3. Stub de DB ───────────────────────────────────────────────────────

import db as db_module                                  # noqa: E402
from tests import _db_stub                              # noqa: E402

db_module.execute_query = _db_stub.fake_execute_query
_db_stub.init()


# ─── 4. Parche del validar_token ─────────────────────────────────────────

from tests import _auth_helpers                         # noqa: E402

_auth_helpers.parchear_validar_token()


# ─── 5. Import de la app (ya con todo parcheado) ─────────────────────────

from app import app as flask_app                        # noqa: E402

flask_app.config["TESTING"] = True


# ─── Re-exports para tests legacy ────────────────────────────────────────
#
# Los tests existentes hacen ``from tests.conftest import (...)``. Los
# re-exportamos acá para no romper esos imports, pero los tests nuevos
# pueden importar directo desde los módulos auxiliares.

from tests._factories import (                          # noqa: E402, F401
    crear_usuario as crear_usuario_db,
    crear_estudiante as crear_perfil_estudiante,
    crear_profesor as crear_perfil_profesor,
)


def login_como(client, usuario, perfiles):
    """Wrapper que rellena ``flask_app`` por vos."""
    return _auth_helpers.login_como(client, usuario, perfiles, flask_app)


# ─── Fixtures de pytest ──────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_db_entre_tests():
    """Limpia la DB y el contador de factories antes de cada test.

    ``autouse=True`` hace que pytest lo aplique a todos los tests
    automáticamente, sin que cada uno tenga que pedirlo. Así garantizamos
    aislamiento sin código repetido."""
    _db_stub.reset()
    from tests import _factories
    _factories.reset_contador()
    yield


@pytest.fixture
def client():
    """Cliente HTTP de prueba de Flask.

    El ``with`` abre el contexto de request del test client y el
    ``yield`` se lo entrega al test. Cuando el test termina, el
    ``__exit__`` del context manager corre y limpia."""
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def admin(client):
    """Usuario admin ya logueado en ``client``."""
    from tests import _factories
    user = _factories.crear_admin(email="admin@test.com", dni=11111111)
    login_como(client, user, ["admin"])
    return user


@pytest.fixture
def alumno_logueado(client):
    """Usuario con perfil estudiante ya logueado."""
    from tests import _factories
    user = _factories.crear_usuario(
        nombre="Ana", apellido="Alumna",
        email="ana@test.com", dni=22222222,
    )
    estudiante = _factories.crear_estudiante(user["id"], padron=100001, carrera="Sistemas")
    login_como(client, user, ["alumno"])
    return {"usuario": user, "estudiante": estudiante}


@pytest.fixture
def docente_logueado(client):
    """Usuario con perfil profesor ya logueado."""
    from tests import _factories
    user = _factories.crear_usuario(
        nombre="Juan", apellido="Docente",
        email="juan@test.com", dni=33333333,
    )
    profesor = _factories.crear_profesor(user["id"], legajo=500001, titulo="Ing. Informática")
    login_como(client, user, ["docente"])
    return {"usuario": user, "profesor": profesor}
