from flask import Blueprint, jsonify, make_response, request

import services.auth_service as logic


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

    nombre = args.get("nombre")
    apellido = args.get("apellido")
    dni = args.get("dni")
    email = args.get("email")
    password = args.get("password")
    rol_id = args.get("rol_id")

    token = logic.crear_usuario(nombre, apellido, dni, email, password, rol_id)

    respuesta = make_response(jsonify({
        "mensaje": "Cuenta creada correctamente",
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

@auth_bp.get("/tipos_usuario") # get tipos de usuario (roles)
def get_user_types(): 
    tipos = logic.get_user_types()

    return jsonify({"tipos": tipos}), 200
