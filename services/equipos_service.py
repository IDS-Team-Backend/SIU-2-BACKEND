import repositories.equipos_repository as db
import repositories.evaluaciones_repository as evaluaciones_db
from utils.error_handlers import (
    NotFoundError,
    ValidationError
)
from utils.validaciones import (
    validar_body_presente,
    validar_entero,
    validar_string_no_vacio
)

equipo_params = [
    "curso_id",
    "evaluacion_id",
    "nombre"
]
equipo_update_params = [
    "curso_id",
    "evaluacion_id",
    "nombre",
    "activo"
]

def obtener_equipos(
    curso_id=None,
    evaluacion_id=None,
    nombre=None,
    activo=None
):
    return db.obtener_equipos(
        curso_id,
        evaluacion_id,
        nombre,
        activo
    )

def crear_equipo(parametros):
    validar_body_presente(parametros)
    for campo in equipo_params:
        if campo not in parametros:
            raise ValidationError(
                f"El campo '{campo}' es requerido."
            )
    curso_id = validar_entero(
        parametros["curso_id"],
        "curso_id"
    )
    evaluacion_id = validar_entero(
        parametros["evaluacion_id"],
        "evaluacion_id"
    )
    nombre = validar_string_no_vacio(
        parametros["nombre"],
        "nombre"
    )
    evaluacion = evaluaciones_db.obtener_evaluacion_por_id(
        evaluacion_id
    )
    if not evaluacion:
        raise NotFoundError(
            "No se encontró la evaluación"
        )
    if not evaluacion["es_grupal"]:
        raise ValidationError(
            "La evaluación no permite equipos."
        )
    return db.crear_equipo(
        curso_id,
        evaluacion_id,
        nombre
    )

def obtener_equipo_por_id(id):
    equipo = db.obtener_equipo_por_id(id)
    if not equipo:
        raise NotFoundError(
            "No se encontró el equipo"
        )

    return equipo

def reemplazar_equipo(id, parametros):
    validar_body_presente(parametros)
    for campo in equipo_update_params:
        if campo not in parametros:
            raise ValidationError(
                f"El campo '{campo}' es requerido."
            )
    curso_id = validar_entero(
        parametros["curso_id"],
        "curso_id"
    )
    evaluacion_id = validar_entero(
        parametros["evaluacion_id"],
        "evaluacion_id"
    )
    nombre = validar_string_no_vacio(
        parametros["nombre"],
        "nombre"
    )
    activo = parametros["activo"]
    evaluacion = evaluaciones_db.obtener_evaluacion_por_id(
        evaluacion_id
    )
    if not evaluacion:
        raise NotFoundError(
            "No se encontró la evaluación"
        )
    if not evaluacion["es_grupal"]:
        raise ValidationError(
            "La evaluación no permite equipos."
        )
    actualizado = db.reemplazar_equipo(
        id,
        curso_id,
        evaluacion_id,
        nombre,
        activo
    )
    if not actualizado:
        raise NotFoundError(
            "No se encontró el equipo"
        )

    return actualizado

def eliminar_equipo(id):
    eliminado = db.eliminar_equipo(id)
    if not eliminado:
        raise NotFoundError(
            "No se encontró el equipo"
        )

    return