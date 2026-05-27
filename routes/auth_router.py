from flask import Blueprint, jsonify, make_response, request

from config import ADMIN, DOCENTE, ALUMNO
import services.auth_service as logic
import repositories.perfiles_repository as perfiles_db
from utils import auth_validator as auth


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")  # iniciar sesion
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


@auth_bp.post("/signup")  # crear cuenta
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


@auth_bp.get("/me/perfiles")  # perfiles del usuario logueado, recalculados desde DB
def get_mis_perfiles():
    auth.validar_token()
    # validar_token ya se ejecutó vía app.before_request global; g.usuario está poblado.
    usuario_id = auth.obtener_usuario_id()
    perfiles = perfiles_db.obtener_perfiles_de_usuario(usuario_id)
    return jsonify({"perfiles": perfiles}), 200
