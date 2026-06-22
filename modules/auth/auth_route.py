from flask import Blueprint, jsonify, make_response, request

from constants import ADMIN, DOCENTE, ALUMNO
from . import auth_service as logic
from . import registro_profesor_service as registro_logic
from . import perfiles_repository as perfiles_db
from modules.usuarios import usuarios_service as usuarios_logic
from utils import auth_validator as auth


auth_public_bp  = Blueprint("auth_public",  __name__)
auth_private_bp = Blueprint("auth_private", __name__)


@auth_public_bp.post("/login")  # iniciar sesion
def login():
    args = request.get_json()

    dni = args.get("dni")
    password = args.get("password")

    token = logic.iniciar_sesion(dni, password)

    respuesta = make_response(jsonify({
        "mensaje": "Sesión iniciada correctamente",
        "token": token
    }))

    respuesta.set_cookie(
        key="access_token_cookie",
        value=token,
        httponly=True,       # el frontend NO puede acceder a ella (seguridad)
        secure=False,        # si es TRUE si o si tiene que ser HTTPS para que se envie la cookie
        samesite="Lax"       # proteccion extra
    )

    return respuesta, 200


@auth_public_bp.post("/signup")  # crear cuenta
def signup(): 
    args = request.get_json()

    new_usuario, token = logic.crear_usuario(args)

    respuesta = make_response(jsonify({
        "usuario": new_usuario,
    }))

    respuesta.set_cookie(
        key="access_token_cookie",
        value=token,
        httponly=True,       # el frontend NO puede acceder a ella (seguridad)
        secure=False,        # si es TRUE si o si tiene que ser HTTPS para que se envie la cookie
        samesite="Lax"       # proteccion extra
    )

    return respuesta, 200

@auth_private_bp.get("/me")  # devuelve el usuario logueado y sus perfiles 
def get_me():
    usuario_id = auth.obtener_usuario_id()
    usuario = logic.get_usuario_completo(usuario_id) # devuelve el usuario y si existe, su ID de profesor o alumno
    perfiles = perfiles_db.obtener_perfiles_de_usuario(usuario_id)
    return jsonify({"usuario": usuario, "perfiles": perfiles}), 200


@auth_public_bp.post("/finalizar-registro")  # el profesor define su contraseña y valida su email
def finalizar_registro():
    data = request.get_json(silent=True) or {}
    registro_logic.finalizar_registro(
        email=data.get("email", ""),
        codigo=data.get("codigo", ""),
        nueva_password=data.get("nueva_password", ""),
        confirmar_password=data.get("confirmar_password", ""),
    )
    return jsonify({"message": "Registración finalizada. Ya podés iniciar sesión."}), 200


@auth_private_bp.get("/me/perfiles")  # perfiles del usuario logueado, recalculados desde DB
def get_mis_perfiles():
    usuario_id = auth.obtener_usuario_id()
    perfiles = perfiles_db.obtener_perfiles_de_usuario(usuario_id)
    return jsonify({"perfiles": perfiles}), 200


# ── Password ──────────────────────────────────────────────────────────────────

from flask import Blueprint, jsonify, request

from . import password_reset_service as logic
from utils import auth_validator as auth
from utils.error_handlers import ValidationError
from config import FRONTEND_URL

# Público: solicitar/confirmar reset (sin sesión).
password_bp = Blueprint("password", __name__)

# Privado: cambiar la propia contraseña (registrado en BLUEPRINTS_PRIVADOS).
password_private_bp = Blueprint("password_private", __name__)


@password_bp.post("/solicitar")
def solicitar():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()

    if not email:
        raise ValidationError("El email es obligatorio.")

    logic.solicitar_reset(email, FRONTEND_URL)

    return jsonify({
        "message": "Si el email está registrado, recibirás un enlace para restablecer tu contraseña."
    }), 200


@password_bp.post("/confirmar")
def confirmar():
    data = request.get_json(silent=True) or {}
    logic.confirmar_reset(
        token=data.get("token", "").strip(),
        nueva_password=data.get("nueva_password", ""),
        confirmar_password=data.get("confirmar_password", ""),
    )
    return jsonify({"message": "Contraseña actualizada correctamente."}), 200


@password_private_bp.post("/cambiar")
def cambiar():
    usuario_id = auth.obtener_usuario_id()
    data = request.get_json(silent=True) or {}
    logic.cambiar_password_autenticado(
        usuario_id=usuario_id,
        password_actual=data.get("password_actual", ""),
        nueva_password=data.get("nueva_password", ""),
        confirmar_password=data.get("confirmar_password", ""),
    )
    return jsonify({"message": "Contraseña cambiada correctamente."}), 200