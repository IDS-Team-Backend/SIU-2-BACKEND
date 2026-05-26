import os
import re

from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
import repositories.usuarios_repository as db
import repositories.estudiantes_repository as estudiantes_db
from utils.error_handlers import NotFoundError, ValidationError
import utils.JWT_handler as TokenHandler
import utils.validators as validator

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

    perfiles = estudiantes_db.obtener_perfiles_de_usuario(usuario["id"])

    token = TokenHandler.create_token(usuario, perfiles)

    return token

def crear_usuario(nombre: str, apellido: str, dni: int, email: str, password: str, rol_id: int):
    if not isinstance(dni, int) or dni <= 0 or len(str(dni)) != 8:
        raise ValidationError("El DNI debe ser un número entero de 8 dígitos")
    
    validacion_email = validator.validar_email(email)
    if not validacion_email["valido"]:
        raise ValidationError(validacion_email["mensaje"])
    
    if len(password) < 6:
        raise ValidationError("La contraseña debe tener al menos 6 caracteres")
    
    if db.get_user_by_dni(dni):
        raise ValidationError("El DNI ya se encuentra registrado")
    
    if db.get_user_by_email(email):
        raise ValidationError("El email ya se encuentra registrado")
    
    if not validator.es_rol_valido(rol_id):
        raise ValidationError("El rol_id no corresponde a un rol válido")

    new_user = db.crear_usuario(nombre, apellido, email, dni, password, rol_id)

    token = TokenHandler.create_token(new_user, [])

    return new_user, token

def get_user_types():
    tipos = db.get_user_types()

    if not tipos:
        raise Exception("No se encontraron tipos de usuario")

    return tipos