import mysql.connector

import repositories.estudiantes_repository as db
import repositories.usuarios_repository as usuarios_db
from utils.error_handlers import NotFoundError, DuplicateError


def obtener_estudiantes(carrera=None, anio_ingreso=None, activo=None,
                        usuario_id=None, page_size=20, offset=0):
    return db.obtener_estudiantes(
        carrera, anio_ingreso, activo, usuario_id,
        page_size=page_size, offset=offset
    )


def crear_estudiante(parametros):
    usuario_id = parametros["usuario_id"]
    padron = parametros["padron"]
    carrera = parametros["carrera"]
    anio_ingreso = parametros["anio_ingreso"]

    if not usuarios_db.obtener_usuario_por_id(usuario_id):
        raise NotFoundError("No se encontró el usuario para crear el perfil estudiante.")

    if db.existe_estudiante_para_usuario(usuario_id):
        raise DuplicateError("Ya existe un perfil estudiante para ese usuario.")

    if db.existe_padron(padron):
        raise DuplicateError("Ya existe un estudiante con ese padrón.")

    try:
        return db.crear_estudiante(usuario_id, padron, carrera, anio_ingreso)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe un estudiante con esos datos.")


def obtener_estudiante_por_id(id):
    estudiante = db.obtener_estudiante_por_id(id)

    if not estudiante:
        raise NotFoundError("No se encontró el estudiante")

    return estudiante


def reemplazar_estudiante(id, parametros):
    padron = parametros["padron"]
    carrera = parametros["carrera"]
    anio_ingreso = parametros["anio_ingreso"]
    activo = parametros["activo"]

    if db.existe_padron(padron, excluir_id=id):
        raise DuplicateError("Ya existe otro estudiante con ese padrón.")

    try:
        return db.reemplazar_estudiante(id, padron, carrera, anio_ingreso, activo)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe otro estudiante con esos datos.")


def eliminar_estudiante(id: int):
    if not db.eliminar_estudiante(id):
        raise NotFoundError("No se encontró el estudiante")

    return
