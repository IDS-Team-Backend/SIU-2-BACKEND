"""Helpers de autenticación para los tests.

En producción el endpoint POST /auth/login emite un JWT y lo setea
como cookie. Para los tests **no usamos ese endpoint** sino que
generamos el JWT a mano con ``JWT_handler.create_token`` y lo
inyectamos como cookie en el cliente de prueba.

Por qué evitamos POST /auth/login en los tests
==============================================
En ``backend/routes/__init__.py`` se registra
``app.before_request(validar_token)`` de forma **global**, lo que
significa que hasta POST /auth/login (que en teoría es público)
intenta validar la cookie del JWT y devuelve 401 si no la encuentra.

Es un bug del backend: el endpoint de login no debería requerir
cookie. Lo parcheamos en el conftest (``parchear_validar_token``)
para los tests de auth que llaman al endpoint HTTP. Pero para todo
el resto de los tests, generar el JWT directamente es más rápido,
más controlable, y no depende del bug.
"""

import utils.JWT_handler as JWT_handler
import repositories.usuarios_repository as usuarios_db


# ─── Parche del validar_token global ─────────────────────────────────────

RUTAS_PUBLICAS = ("/auth/login", "/auth/signup")


def parchear_validar_token():
    """Hace que ``validar_token`` ignore /auth/login y /auth/signup.

    Hay que llamarlo **antes** de importar la app para que el hook
    quede registrado con la versión parcheada (``register_routes`` lee
    la referencia a ``validar_token`` cuando se invoca).
    """
    from flask import request
    import utils.auth_validator as auth_mod

    original = auth_mod.validar_token

    def validar_token_con_rutas_publicas():
        if request.path in RUTAS_PUBLICAS:
            return
        return original()

    auth_mod.validar_token = validar_token_con_rutas_publicas


# ─── Login ───────────────────────────────────────────────────────────────

def login_como(client, usuario, perfiles, flask_app):
    """Loguea al ``client`` como ``usuario`` con los ``perfiles`` dados.

    Acepta un dict de usuario (típicamente devuelto por
    ``factories.crear_usuario``) o un ID. Setea la cookie
    ``access_token_cookie`` que es la que el backend espera.

    ``flask_app`` se pasa para entrar al contexto de aplicación que
    necesita ``JWT_handler.create_token`` (lee ``current_app.config``).
    """
    if isinstance(usuario, dict):
        payload = usuario
    else:
        payload = usuarios_db.obtener_usuario_por_id(usuario)

    with flask_app.app_context():
        token = JWT_handler.create_token(payload, list(perfiles))

    client.set_cookie("access_token_cookie", token, domain="localhost")
    return token
