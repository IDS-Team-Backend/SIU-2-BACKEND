from . import entregas_repository as db
from modules.evaluaciones import evaluaciones_repository as evaluaciones_db
from modules.estudiantes import estudiantes_repository as estudiantes_db
from modules.equipos import equipos_repository as equipos_db
from constants import ESTADOS_ENTREGA
from utils.error_handlers import (
    ValidationError,
    NotFoundError,
    DuplicateError
)
from utils.validaciones import (
    validar_body_presente,
    validar_entero
)

entrega_params = [
    "evaluacion_id",
    "fecha_entrega"
]

def obtener_entregas(evaluacion_id=None, alumno_id=None, equipo_id=None):
    return db.obtener_entregas(
        evaluacion_id,
        alumno_id,
        equipo_id
    )

def crear_entrega(parametros):
    validar_body_presente(parametros)
    for campo in entrega_params:
        if campo not in parametros:
            raise ValidationError(
                f"El campo '{campo}' es requerido."
            )

    evaluacion_id = validar_entero(
        parametros["evaluacion_id"],
        "evaluacion_id"
    )
    fecha_entrega = parametros["fecha_entrega"]
    estado = parametros.get("estado", ESTADOS_ENTREGA[0])
    if estado not in ESTADOS_ENTREGA:
        raise ValidationError(
            f"Estado inválido. Debe ser uno de: {', '.join(ESTADOS_ENTREGA)}."
        )
    archivo_url = parametros.get("archivo_url")
    observaciones = parametros.get("observaciones")

    evaluacion = evaluaciones_db.obtener_evaluacion_por_id(evaluacion_id)
    if not evaluacion:
        raise NotFoundError("No se encontró la evaluación")

    alumno_id = parametros.get("alumno_id")
    equipo_id = parametros.get("equipo_id")

    if evaluacion["es_grupal"]:
        if not equipo_id:
            raise ValidationError("Las evaluaciones grupales requieren equipo_id.")
        equipo = equipos_db.obtener_equipo_por_id(equipo_id)
        if not equipo:
            raise NotFoundError("No se encontró el equipo")
        if db.existe_entrega_equipo(evaluacion_id, equipo_id):
            raise DuplicateError("El equipo ya tiene una entrega registrada.")

        return db.crear_entrega_grupal(
            evaluacion_id,
            equipo_id,
            fecha_entrega,
            estado,
            archivo_url,
            observaciones
        )
    else:
        if not alumno_id:
            raise ValidationError("Las evaluaciones individuales requieren alumno_id.")
        alumno = estudiantes_db.obtener_estudiante_por_id(alumno_id)
        if not alumno:
            raise NotFoundError("No se encontró el alumno")
        if db.existe_entrega_alumno(evaluacion_id, alumno_id):
            raise DuplicateError("El alumno ya tiene una entrega registrada.")

        return db.crear_entrega_individual(
            evaluacion_id,
            alumno_id,
            fecha_entrega,
            estado,
            archivo_url,
            observaciones
        )

def obtener_entrega_por_id(id):
    entrega = db.obtener_entrega_por_id(id)
    if not entrega:
        raise NotFoundError(
            "No se encontró la entrega"
        )
    return entrega

def actualizar_entrega(id, parametros):
    validar_body_presente(parametros)
    if "estado" in parametros and parametros["estado"] not in ESTADOS_ENTREGA:
        raise ValidationError(
            f"Estado inválido. Debe ser uno de: {', '.join(ESTADOS_ENTREGA)}."
        )

    campos = {
        campo: valor
        for campo, valor in parametros.items()
        if campo in db.CAMPOS_ACTUALIZABLES
    }
    if not campos:
        raise ValidationError(
            "No se enviaron campos válidos para actualizar."
        )

    entrega = db.obtener_entrega_por_id(id)
    if not entrega:
        raise NotFoundError(
            "No se encontró la entrega"
        )

    db.actualizar_entrega(id, campos)
    return db.obtener_entrega_por_id(id)

def eliminar_entrega(id):
    eliminado = db.eliminar_entrega(id)
    if not eliminado:
        raise NotFoundError(
            "No se encontró la entrega"
        )

    return
