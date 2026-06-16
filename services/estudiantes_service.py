import mysql.connector

import repositories.estudiantes_repository as db
import repositories.usuarios_repository as usuarios_db
import repositories.estudiante_curso_repository as estudiante_curso_db
from constants import ADMIN
from utils import auth_validator as auth
from utils.error_handlers import NotFoundError, DuplicateError, ForbiddenError


CAMPOS_PATCH_ADMIN = ("padron", "carrera", "anio_ingreso", "activo")
CAMPOS_PATCH_SELF = ("carrera",)


def _es_propio_estudiante(estudiante):
    return bool(estudiante) and estudiante["usuario_id"] == auth.obtener_usuario_id()


def obtener_estudiantes(carrera=None, anio_ingreso=None,
                        usuario_id=None, q=None, eliminados=False, page_size=20, offset=0):
    return db.obtener_estudiantes(
        carrera, anio_ingreso, usuario_id, q=q, eliminados=eliminados,
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
    activo = parametros["activo"]

    if db.existe_padron(padron, excluir_id=id):
        raise DuplicateError("Ya existe otro estudiante con ese padrón.")

    try:
        return db.reemplazar_estudiante(id, padron, carrera, anio_ingreso, activo)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe otro estudiante con esos datos.")


def modificar_estudiante_parcial(id, parametros):
    estudiante = db.obtener_estudiante_por_id(id)
    if not estudiante:
        raise NotFoundError("No se encontró el estudiante")

    es_admin = auth.usuario_es(ADMIN)
    es_propio = _es_propio_estudiante(estudiante)

    if not es_admin and not es_propio:
        raise ForbiddenError("No tenés permisos para modificar este estudiante.")

    if not es_admin:
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

    # Al dar de baja al estudiante, se lo desvincula de todos los cursos
    # en los que estuviera inscripto.
    estudiante_curso_db.eliminar_por_estudiante(id)
    return


def reactivar_estudiante(id: int):
    if not db.reactivar_estudiante(id):
        raise NotFoundError("No se encontró el estudiante eliminado")
    return


def eliminar_estudiantes_lote(ids):
    if not isinstance(ids, list) or not ids:
        raise ValueError("Se requiere una lista no vacía de estudiante_ids.")

    eliminados, errores = db.eliminar_estudiantes_lote(ids)

    for est_id in ids:
        try:
            estudiante_curso_db.eliminar_por_estudiante(int(est_id))
        except (ValueError, TypeError):
            continue

    return {
        "procesados_exito": eliminados,
        "ignorados_duplicados": 0,
        "errores_encontrados": len(errores),
        "detalles_errores": errores,
    }


def reactivar_estudiantes_lote(ids):
    if not isinstance(ids, list) or not ids:
        raise ValueError("Se requiere una lista no vacía de estudiante_ids.")

    reactivados, errores = db.reactivar_estudiantes_lote(ids)
    return {
        "procesados_exito": reactivados,
        "ignorados_duplicados": 0,
        "errores_encontrados": len(errores),
        "detalles_errores": errores,
    }
