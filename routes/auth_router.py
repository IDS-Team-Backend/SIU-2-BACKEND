from flask import Blueprint, jsonify, make_response, request

from constants import ADMIN, DOCENTE, ALUMNO
import services.auth_service as logic
import services.registro_profesor_service as registro_logic
import repositories.perfiles_repository as perfiles_db
import services.usuarios_service as usuarios_logic
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
