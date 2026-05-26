from functools import wraps

from flask import g, jsonify, request
from config import ADMIN, DOCENTE
from utils import JWT_handler
from utils.validators import id_rol_a_nombre
from utils.error_handlers import ForbiddenError, UnauthorizedError

# esta funcion se tiene que ejecutar en @before_request
def validar_token():
    try:
        # 'g' es una variable global temporal de FLASK
        # existe desde que se recibe la request (entra al router) y hasta que se devuelve la response (return del router)

        token = request.cookies.get("access_token_cookie")

        if not token:
            raise UnauthorizedError("No se encontró un token de autenticación en la cookie.")

        # valida si el token es correcto y devuelve el payload del mismo (nombre, apellido, rol_id)
        g.usuario = JWT_handler.decode_token(token) 

    except Exception as e:
        raise UnauthorizedError(str(e))
    

ROLES_LEGACY = {
    1: "admin",
    2: "profesor",
    3: "alumno",
    4: "ayudante",
}

def requiere_roles(*roles_permitidos):
    def decorador(f):
        @wraps(f)
        def funcion_decorada(*args, **kwargs):
            perfiles = set(g.usuario.get("perfiles") or [])

            rol_usuario = ROLES.get(id_rol_usuario)

            if not perfiles.intersection(roles_permitidos):
                raise ForbiddenError("Acceso denegado. No tenés los permisos necesarios.")

            return f(*args, **kwargs)
        return funcion_decorada
    return decorador

def usuario_es(rol):
    id_rol_usuario = g.usuario.get("rol_id")
    rol_usuario = id_rol_a_nombre(id_rol_usuario)
    return rol_usuario == rol

def obtener_usuario_id():
    return g.usuario.get("id")