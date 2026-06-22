import mysql.connector

from . import curso_docentes_repository as db
from modules.cursada.cursos import cursos_repository as cursos_db
from modules.personas.profesores import profesores_repository as profesores_db
from config import ROLES_DOCENTE_CATEDRA
from utils.error_handlers import NotFoundError, DuplicateError, ValidationError


def _validar_rol(rol):
    if rol not in ROLES_DOCENTE_CATEDRA:
        raise ValidationError(
            f"El tipo de participación debe ser uno de: {', '.join(ROLES_DOCENTE_CATEDRA)}."
        )


def obtener_equipo_docente(curso_id):
    if not cursos_db.obtener_curso_por_id(curso_id):
        raise NotFoundError("No se encontró el curso.")
    return db.obtener_por_curso(curso_id)


def obtener_participaciones_por_docentes(docente_ids):
    """Cursos en los que participa cada docente (con su rol), batcheado."""
    ids = [d for d in docente_ids if isinstance(d, int)]
    if not ids:
        return []
    return db.obtener_por_docentes(ids)


def agregar_integrante(curso_id, docente_id, rol):
    _validar_rol(rol)

    if not cursos_db.obtener_curso_por_id(curso_id):
        raise NotFoundError("No se encontró el curso.")

    if not profesores_db.obtener_profesor_por_id(docente_id):
        raise NotFoundError("No se encontró el profesor.")

    if db.existe(curso_id, docente_id):
        raise DuplicateError("Ese profesor ya es integrante del curso.")

    try:
        return db.agregar(curso_id, docente_id, rol)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ese profesor ya es integrante del curso.")


def cambiar_participacion(id, rol):
    _validar_rol(rol)

    if not db.obtener_por_id(id):
        raise NotFoundError("No se encontró el integrante.")

    db.cambiar_rol(id, rol)
    return db.obtener_por_id(id)


def quitar_integrante(id):
    if not db.eliminar(id):
        raise NotFoundError("No se encontró el integrante.")
