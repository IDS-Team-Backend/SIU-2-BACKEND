import repositories.evaluaciones_repository as db
import validators.evaluaciones_validator as evaluaciones_validator
from utils.error_handlers import NotFoundError


def obtener_evaluaciones(curso_id=None, tipo_evaluacion_id=None, titulo=None, fecha=None, activo=None):
    return db.obtener_evaluaciones(curso_id, tipo_evaluacion_id, titulo, fecha, activo)


def crear_evaluacion(parametros):
    datos = evaluaciones_validator.validar_body_crear_evaluacion(parametros)
    return db.crear_evaluacion(
        datos["curso_id"],
        datos["tipo_evaluacion_id"],
        datos["titulo"],
        datos["descripcion"],
        datos["fecha"],
    )


def obtener_evaluacion_por_id(id):
    evaluacion = db.obtener_evaluacion_por_id(id)
    if not evaluacion:
        raise NotFoundError("No se encontró la evaluación")
    return evaluacion


def reemplazar_evaluacion(id, parametros):
    datos = evaluaciones_validator.validar_body_reemplazar_evaluacion(parametros)
    actualizado = db.reemplazar_evaluacion(
        id,
        datos["curso_id"],
        datos["tipo_evaluacion_id"],
        datos["titulo"],
        datos["descripcion"],
        datos["fecha"],
        datos["activo"],
    )
    if not actualizado:
        raise NotFoundError("No se encontró la evaluación")
    return actualizado


def eliminar_evaluacion(id):
    eliminado = db.eliminar_evaluacion(id)
    if not eliminado:
        raise NotFoundError("No se encontró la evaluación")
    return
