import mysql.connector

from . import estudiantes_repository as db
from modules.usuarios import usuarios_repository as usuarios_db
from constants import ADMIN
from utils import auth_validator as auth
from utils.error_handlers import NotFoundError, DuplicateError, ForbiddenError


CAMPOS_PATCH_ADMIN = ("padron", "carrera", "anio_ingreso")
CAMPOS_PATCH_SELF = ("carrera",)


def _es_propio_estudiante(estudiante):
    return bool(estudiante) and estudiante["usuario_id"] == auth.obtener_usuario_id()


def obtener_estudiantes(carrera=None, anio_ingreso=None,
                        usuario_id=None, q=None, page_size=20, offset=0):
    return db.obtener_estudiantes(
        carrera=carrera,
        anio_ingreso=anio_ingreso,
        usuario_id=usuario_id,
        q=q,
        page_size=page_size,
        offset=offset,
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
        estudiante_nuevo = db.crear_estudiante(usuario_id, padron, carrera, anio_ingreso)
        return estudiante_nuevo

    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe un estudiante con esos datos.")


def obtener_estudiante_por_id(id):
    estudiante = db.obtener_estudiante_por_id(id)

    if not estudiante:
        raise NotFoundError("No se encontró el estudiante")

    return estudiante


def obtener_estudiante_por_padron(padron):
    estudiante = db.obtener_estudiante_por_padron(padron)
    if not estudiante:
        raise NotFoundError(f"No se encontró ningún estudiante con el padrón {padron}")
    return estudiante


def obtener_estudiante_me():
    usuario_id = auth.obtener_usuario_id()
    estudiante = db.obtener_estudiante_por_usuario_id(usuario_id)
    if not estudiante:
        raise NotFoundError("El usuario no tiene un perfil estudiante asociado.")
    return estudiante


def reemplazar_estudiante(id, parametros):
    padron = parametros["padron"]
    carrera = parametros["carrera"]
    anio_ingreso = parametros["anio_ingreso"]

    if db.existe_padron(padron, excluir_id=id):
        raise DuplicateError("Ya existe otro estudiante con ese padrón.")

    try:
        return db.reemplazar_estudiante(id, padron, carrera, anio_ingreso)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe otro estudiante con esos datos.")


def modificar_estudiante_parcial(id, parametros):
    estudiante = db.obtener_estudiante_por_id(id)
    if not estudiante:
        raise NotFoundError("No se encontró el estudiante")

    es_staff = auth.usuario_es_staff()
    es_propio = _es_propio_estudiante(estudiante)

    if not es_staff and not es_propio:
        raise ForbiddenError("No tenés permisos para modificar este estudiante.")

    if not es_staff:
        keys_no_permitidas = set(parametros.keys()) - set(CAMPOS_PATCH_SELF)
        if keys_no_permitidas:
            raise ForbiddenError(
                f"Sólo podés modificar los campos: {', '.join(CAMPOS_PATCH_SELF)}."
            )

    if "padron" in parametros and db.existe_padron(parametros["padron"], excluir_id=id):
        raise DuplicateError("Ya existe otro estudiante con ese padrón.")

    try:
        actualizado = db.modificar_estudiante_parcial(id, parametros)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe otro estudiante con esos datos.")

    if actualizado is None:
        raise NotFoundError("No se encontró el estudiante")

    return actualizado


def eliminar_estudiante(id: int, hard_delete=False):
    if not db.eliminar_estudiante(id, hard=hard_delete):
        raise NotFoundError("No se encontró el estudiante")

    return
