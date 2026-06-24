import repositories.equipo_integrantes_repository as db
import repositories.equipos_repository as equipos_db
import repositories.estudiantes_repository as estudiantes_db
from utils.error_handlers import (
    ValidationError,
    NotFoundError,
    DuplicateError
)
from utils.validaciones import (
    validar_body_presente,
    validar_entero
)

integrante_params = [
    "equipo_id",
    "alumno_id"
]

def obtener_integrantes(equipo_id=None,alumno_id=None):
    return db.obtener_integrantes(equipo_id,alumno_id)

def agregar_integrante(parametros):
    validar_body_presente(parametros)
    for campo in integrante_params:
        if campo not in parametros:
            raise ValidationError(
                f"El campo '{campo}' es requerido."
            )
    equipo_id = validar_entero(
        parametros["equipo_id"],
        "equipo_id"
    )
    alumno_id = validar_entero(
        parametros["alumno_id"],
        "alumno_id"
    )
    equipo = equipos_db.obtener_equipo_por_id(
        equipo_id
    )
    if not equipo:
        raise NotFoundError(
            "No se encontró el equipo"
        )
    alumno = estudiantes_db.obtener_estudiante_por_id(
        alumno_id
    )
    if not alumno:
        raise NotFoundError(
            "No se encontró el alumno"
        )
    if db.existe_integrante(
        equipo_id,
        alumno_id
    ):
        raise DuplicateError(
            "El alumno ya pertenece al equipo."
        )
    return db.agregar_integrante(
        equipo_id,
        alumno_id
    )


def eliminar_integrante(equipo_id,alumno_id):
    eliminado = db.eliminar_integrante(equipo_id,alumno_id)
    if not eliminado:
        raise NotFoundError(
            "No se encontró el integrante"
        )
    return