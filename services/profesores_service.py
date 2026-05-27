import mysql.connector

import repositories.profesores_repository as db
import repositories.usuarios_repository as usuarios_db
from config import ADMIN
from utils import auth_validator as auth
from utils.error_handlers import NotFoundError, DuplicateError, ForbiddenError


CAMPOS_PATCH_ADMIN = ("legajo", "titulo", "departamento", "fecha_ingreso", "activo")
CAMPOS_PATCH_SELF = ("titulo", "departamento")


def _es_propio_profesor(profesor):
    return bool(profesor) and profesor["usuario_id"] == auth.obtener_usuario_id()


def obtener_profesores(departamento=None, titulo=None, activo=None,
                       usuario_id=None, page_size=20, offset=0):
    return db.obtener_profesores(
        departamento, titulo, activo, usuario_id,
        page_size=page_size, offset=offset,
    )


def crear_profesor(parametros):
    usuario_id = parametros["usuario_id"]
    legajo = parametros["legajo"]
    titulo = parametros["titulo"]
    departamento = parametros["departamento"]
    fecha_ingreso = parametros["fecha_ingreso"]

    if not usuarios_db.obtener_usuario_por_id(usuario_id):
        raise NotFoundError("No se encontró el usuario para crear el perfil profesor.")

    if db.existe_profesor_para_usuario(usuario_id):
        raise DuplicateError("Ya existe un perfil profesor para ese usuario.")

    if db.existe_legajo(legajo):
        raise DuplicateError("Ya existe un profesor con ese legajo.")

    try:
        return db.crear_profesor(usuario_id, legajo, titulo, departamento, fecha_ingreso)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe un profesor con esos datos.")


def obtener_profesor_por_id(id):
    profesor = db.obtener_profesor_por_id(id)
    if not profesor:
        raise NotFoundError("No se encontró el profesor")
    return profesor


def obtener_profesor_me():
    usuario_id = auth.obtener_usuario_id()
    profesor = db.obtener_profesor_por_usuario_id(usuario_id)
    if not profesor:
        raise NotFoundError("El usuario no tiene un perfil profesor asociado.")
    return profesor


def reemplazar_profesor(id, parametros):
    legajo = parametros["legajo"]
    titulo = parametros["titulo"]
    departamento = parametros["departamento"]
    fecha_ingreso = parametros["fecha_ingreso"]
    activo = parametros["activo"]

    if db.existe_legajo(legajo, excluir_id=id):
        raise DuplicateError("Ya existe otro profesor con ese legajo.")

    try:
        return db.reemplazar_profesor(id, legajo, titulo, departamento, fecha_ingreso, activo)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe otro profesor con esos datos.")


def modificar_profesor_parcial(id, parametros):
    profesor = db.obtener_profesor_por_id(id)
    if not profesor:
        raise NotFoundError("No se encontró el profesor")

    es_admin = auth.usuario_es(ADMIN)
    es_propio = _es_propio_profesor(profesor)

    if not es_admin and not es_propio:
        raise ForbiddenError("No tenés permisos para modificar este profesor.")

    if not es_admin:
        keys_no_permitidas = set(parametros.keys()) - set(CAMPOS_PATCH_SELF)
        if keys_no_permitidas:
            raise ForbiddenError(
                f"Sólo podés modificar los campos: {', '.join(CAMPOS_PATCH_SELF)}."
            )

    if "legajo" in parametros and db.existe_legajo(parametros["legajo"], excluir_id=id):
        raise DuplicateError("Ya existe otro profesor con ese legajo.")

    try:
        actualizado = db.modificar_profesor_parcial(id, parametros)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe otro profesor con esos datos.")

    if actualizado is None:
        raise NotFoundError("No se encontró el profesor")

    return actualizado


def eliminar_profesor(id: int):
    if not db.eliminar_profesor(id):
        raise NotFoundError("No se encontró el profesor")
    return
