import mysql.connector

import repositories.usuarios_repository as db
from utils import auth_validator as auth
from config import ADMIN, DOCENTE, ALUMNO
from utils.error_handlers import NotFoundError, ValidationError, DuplicateError, ForbiddenError


usuario_params = ["nombre", "apellido", "dni", "email", "password"]
usuario_update_params = ["nombre", "apellido", "dni", "email", "activo"]


def obtener_usuarios(nombre=None, apellido=None, email=None, dni=None, rol=None):
    if rol and rol not in [ADMIN, ALUMNO, DOCENTE, "pendiente"]:
        raise ValidationError("El rol debe ser 'admin', 'alumno', 'docente' o 'pendiente'.")
    
    if rol and not auth.usuario_es(ADMIN):
        raise ForbiddenError("Solo un admin puede filtrar por rol.")

    return db.obtener_usuarios(nombre, apellido, email, dni, rol)


def crear_usuario(parametros):
    for campo in usuario_params:
        if (campo not in parametros) or (not parametros[campo]):
            raise ValidationError(f"El campo '{campo}' es requerido.")

    nombre = parametros["nombre"]
    apellido = parametros["apellido"]
    email = parametros["email"]
    dni = parametros["dni"]
    password = parametros["password"]
    es_admin = bool(parametros.get("es_admin", False))

    if es_admin and not auth.usuario_es(ADMIN):
        raise ForbiddenError("Solo un admin puede crear otro admin.")

    if db.existe_email(email):
        raise DuplicateError("Ya existe un usuario con ese email.")
    if db.existe_dni(dni):
        raise DuplicateError("Ya existe un usuario con ese DNI.")

    try:
        return db.crear_usuario(nombre, apellido, email, dni, password, es_admin)
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
        if campo not in parametros:
            raise ValidationError(f"El campo '{campo}' es requerido.")

    nombre = parametros["nombre"]
    apellido = parametros["apellido"]
    email = parametros["email"]
    dni = parametros["dni"]
    activo = parametros.get("activo", True)
    es_admin = bool(parametros.get("es_admin", False))

    if es_admin and not auth.usuario_es(ADMIN):
        raise ForbiddenError("Solo un admin puede asignar el flag es_admin.")

    if db.existe_email(email, excluir_id=id):
        raise DuplicateError("Ya existe otro usuario con ese email.")
    if db.existe_dni(dni, excluir_id=id):
        raise DuplicateError("Ya existe otro usuario con ese DNI.")

    try:
        return db.reemplazar_usuario(id, nombre, apellido, email, dni, es_admin, activo)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe otro usuario con ese email.")