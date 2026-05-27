from werkzeug.security import check_password_hash

import repositories.usuarios_repository as db
import repositories.perfiles_repository as perfiles_db
import validators.usuarios_validator as usuarios_validator
import utils.JWT_handler as TokenHandler
from utils.error_handlers import NotFoundError, ValidationError


def iniciar_sesion(body):
    datos = usuarios_validator.validar_body_login(body)
    dni = datos["dni"]
    password = datos["password"]

    usuario = db.get_user_by_dni(dni)

    if not usuario:
        raise NotFoundError("El DNI no corresponde a ningún usuario registrado")

    if not usuario["activo"]:
        raise ValidationError("El usuario esta dado de baja")

    if not check_password_hash(usuario["password_hash"], password):
        raise ValidationError("Contraseña incorrecta")

    perfiles = perfiles_db.obtener_perfiles_de_usuario(usuario["id"])

    token = TokenHandler.create_token(usuario, perfiles)

    return token


def crear_usuario(body):
    datos = usuarios_validator.validar_body_signup(body)

    if db.get_user_by_dni(datos["dni"]):
        raise ValidationError("El DNI ya se encuentra registrado")

    if db.get_user_by_email(datos["email"]):
        raise ValidationError("El email ya se encuentra registrado")

    new_user = db.crear_usuario(
        datos["nombre"], datos["apellido"], datos["email"], datos["dni"], datos["password"], False
    )

    token = TokenHandler.create_token(new_user, [])

    return new_user, token
