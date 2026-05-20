import os
import re

from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
import repositories.usuarios_repository as db 
from utils.error_handlers import NotFoundError, ValidationError
import utils.JWT_handler as TokenHandler

load_dotenv()

dominios_raw = os.getenv("DOMINIOS_EMAIL_PERMITIDOS", "gmail.com")
DOMINIOS_PERMITIDOS = [dominio.strip().lower() for dominio in dominios_raw.split(',')] # pasar del formato .env a una lista de python

def validar_email(email: str):
    if not email:
        return {"valido": False, "mensaje": "El campo email no puede estar vacío."}

    # verifica: 'texto + @ + texto + . + texto'  mediante regex
    patron_formato = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(patron_formato, email):
        return {"valido": False, "mensaje": "El formato del email es incorrecto (ejemplo válido: usuario@dominio.com)."}

    # extrae el dominio
    partes = email.split('@')
    dominio = partes[1].lower()

    print(dominio, DOMINIOS_PERMITIDOS, flush=True)
    # compara el dominio
    if dominio not in DOMINIOS_PERMITIDOS:
        return {"valido": False, "mensaje": f"El dominio '@{dominio}' no está permitido en esta institución."}

    return {"valido": True, "mensaje": ""}

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
    
    token = TokenHandler.create_token(usuario)

    return token

def crear_usuario(nombre: str, apellido: str, dni: int, email: str, password: str, rol_id: int):
    if not isinstance(dni, int) or dni <= 0 or len(str(dni)) != 8:
        raise ValidationError("El DNI debe ser un número entero de 8 dígitos")
    
    validacion_email = validar_email(email)
    if not validacion_email["valido"]:
        raise ValidationError(validacion_email["mensaje"])
    
    if len(password) < 6:
        raise ValidationError("La contraseña debe tener al menos 6 caracteres")
    
    if db.get_user_by_dni(dni):
        raise ValidationError("El DNI ya se encuentra registrado")
    
    if db.get_user_by_email(email):
        raise ValidationError("El email ya se encuentra registrado")

    new_user = db.crear_usuario(nombre, apellido, dni, email, password, rol_id)

    token = TokenHandler.create_token(new_user)

    return token

def get_user_types():
    tipos = db.get_user_types()

    if not tipos:
        raise Exception("No se encontraron tipos de usuario")

    return tipos