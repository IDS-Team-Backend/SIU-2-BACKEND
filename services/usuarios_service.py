import repositories.usuarios_repository as db 
from utils.error_handlers import NotFoundError, ValidationError, DuplicateError
import mysql.connector

global usuario_params
usuario_params = ["nombre","apellido","padron","email","password","tipo_usuario_id"]

usuario_update_params = ["nombre","apellido","padron","email","tipo_usuario_id","activo"]

def obtener_usuarios(nombre=None, apellido=None ,email=None, padron=None, tipo_usuario_id=None):
   return db.obtener_usuarios(nombre, apellido, email, padron, tipo_usuario_id)
    

def crear_usuario(parametros):
    for campo in usuario_params:
        if (campo not in parametros) or (not parametros[campo]):
            raise ValidationError(f"El campo '{campo}' es requerido.")

    nombre = parametros["nombre"]
    apellido = parametros["apellido"]
    email = parametros["email"]
    padron = parametros["padron"]
    password = parametros["password"]
    tipo_usuario_id = parametros["tipo_usuario_id"]

    if db.existe_email(email):
        raise DuplicateError("Ya existe un usuario con ese email.")
    if db.existe_padron(padron):
        raise DuplicateError("Ya existe un usuario con ese padrón.")

    try:
        return db.crear_usuario(nombre, apellido, email, padron, password, tipo_usuario_id)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe un usuario con ese email.")


def obtener_usuario_por_id(id):
    usuario = db.obtener_usuario_por_id(id)
    
    if not usuario:
        raise NotFoundError("No se encontró el usuario")
    
    return usuario

def eliminar_usuario(id: int):   

    if not db.eliminar_usuario(id):
        raise NotFoundError("No se encontró el usuario")
        
    return 

def reemplazar_usuario(id, parametros):
    for campo in usuario_update_params:
        if (campo not in parametros) or (not parametros[campo]):
            raise ValidationError(f"El campo '{campo}' es requerido.")

    nombre = parametros["nombre"]
    apellido = parametros["apellido"]
    email = parametros["email"]
    padron = parametros["padron"]
    tipo_usuario_id = parametros["tipo_usuario_id"]
    activo = parametros.get("activo", True)

    if db.existe_email(email, excluir_id=id):
        raise DuplicateError("Ya existe otro usuario con ese email.")
    if db.existe_padron(padron, excluir_id=id):
        raise DuplicateError("Ya existe otro usuario con ese padrón.")

    try:
        return db.reemplazar_usuario(id, nombre, apellido, email, padron, tipo_usuario_id, activo)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe otro usuario con ese email.")