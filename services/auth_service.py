from werkzeug.security import check_password_hash

import repositories.usuarios_repository as db
import repositories.perfiles_repository as perfiles_db
from utils.error_handlers import NotFoundError, ValidationError
import utils.JWT_handler as TokenHandler
import utils.validators as validator

signup_required_fields = ["nombre", "apellido", "dni", "email", "password"]

def iniciar_sesion(dni, password):
    if not isinstance(dni, int):
        raise ValidationError("El DNI debe ser un número entero")

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

def validar_datos_usuario(nombre, apellido, dni, email, password):
    if not isinstance(nombre, str):
        raise ValidationError("El nombre debe ser un texto")

    if not isinstance(apellido, str):
        raise ValidationError("El apellido debe ser un texto")

    if not isinstance(email, str) or not email.strip():
        raise ValidationError("El email debe ser un texto")

    if not isinstance(password, str) or not password:
        raise ValidationError("La contraseña debe ser un texto")

    if not isinstance(dni, int) or dni <= 0 or len(str(dni)) != 8:
        raise ValidationError("El DNI debe ser un número entero de 8 dígitos")

    validacion_email = validator.validar_email(email)
    if not validacion_email["valido"]:
        raise ValidationError(validacion_email["mensaje"])
    
    if len(nombre) < 4 or len(nombre) > 20 or not nombre.strip():
        raise ValidationError("El nombre debe tener entre 4 y 20 caracteres")
    
    if len(apellido) < 4 or len(apellido) > 20 or not apellido.strip():
        raise ValidationError("El apellido debe tener entre 4 y 20 caracteres")

    if len(password) < 6:
        raise ValidationError("La contraseña debe tener al menos 6 caracteres")

def crear_usuario(args):
    for campo in signup_required_fields:
        if campo not in args:
            raise ValidationError(f"Falta el campo requerido: {campo}")

    nombre = args.get("nombre")
    apellido = args.get("apellido")
    dni = args.get("dni")
    email = args.get("email")
    password = args.get("password")

    validar_datos_usuario(nombre, apellido, dni, email, password)

    if db.get_user_by_dni(dni):
        raise ValidationError("El DNI ya se encuentra registrado")

    if db.get_user_by_email(email):
        raise ValidationError("El email ya se encuentra registrado")

    new_user = db.crear_usuario(nombre, apellido, email, dni, password)

    token = TokenHandler.create_token(new_user, [])

    return new_user, token
