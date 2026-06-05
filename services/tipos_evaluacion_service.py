from repositories.tipos_evaluacion_repository import *

from utils.error_handlers import (
    ValidationError,
    NotFoundError
)

from utils.error_handlers import (
    ValidationError,
    NotFoundError,
)

def listar_tipos_evaluacion():
    return obtener_tipos_evaluacion()

def crear_nuevo_tipo_evaluacion(
    nombre,
    es_grupal
):
    nombre = nombre.strip()

    if not nombre:
        raise ValidationError(
            "El nombre es obligatorio."
        )

    return crear_tipo_evaluacion(
        nombre,
        es_grupal
    )

def actualizar_tipo_evaluacion_service(
    tipo_evaluacion_id,
    nombre,
    es_grupal
):
    tipo = obtener_tipo_evaluacion_por_id(
        tipo_evaluacion_id
    )

    if not tipo:
        raise NotFoundError(
            "Tipo de evaluación inexistente."
        )

    nombre = nombre.strip()

    if not nombre:
        raise ValidationError(
            "El nombre es obligatorio."
        )

    actualizar_tipo_evaluacion(
        tipo_evaluacion_id,
        nombre,
        es_grupal
    )

def eliminar_tipo_evaluacion_service(
    tipo_evaluacion_id
):
    tipo = obtener_tipo_evaluacion_por_id(
        tipo_evaluacion_id
    )

    if not tipo:
        raise NotFoundError(
            "Tipo de evaluación inexistente."
        )

    eliminar_tipo_evaluacion(
        tipo_evaluacion_id
    )