import repositories.usuarios_repository as db 
from utils.error_handlers import NotFoundError, ValidationError, DuplicateError
import mysql.connector

global usuario_params
usuario_params = ["nombre","apellido","dni","email","password","rol_id"]

usuario_update_params = ["nombre","apellido","dni","email","rol_id","activo"]

def obtener_usuarios(nombre=None, apellido=None ,email=None, dni=None, rol_id=None):
   return db.obtener_usuarios(nombre, apellido, email, dni, rol_id)
    

def crear_usuario(parametros):
    for campo in usuario_params:
        if (campo not in parametros) or (not parametros[campo]):
            raise ValidationError(f"El campo '{campo}' es requerido.")

    nombre = parametros["nombre"]
    apellido = parametros["apellido"]
    email = parametros["email"]
    dni = parametros["dni"]
    password = parametros["password"]
    rol_id = parametros["rol_id"]

    if db.existe_email(email):
        raise DuplicateError("Ya existe un usuario con ese email.")
    if db.existe_dni(dni):
        raise DuplicateError("Ya existe un usuario con ese padrón.")

    try:
        return db.crear_usuario(nombre, apellido, email, dni, password, rol_id)
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
    dni = parametros["dni"]
    rol_id = parametros["rol_id"]
    activo = parametros.get("activo", True)

    if db.existe_email(email, excluir_id=id):
        raise DuplicateError("Ya existe otro usuario con ese email.")
    if db.existe_dni(dni, excluir_id=id):
        raise DuplicateError("Ya existe otro usuario con ese padrón.")

    try:
        return db.reemplazar_usuario(id, nombre, apellido, email, dni, rol_id, activo)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe otro usuario con ese email.")