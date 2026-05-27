import repositories.evaluaciones_repository as db
import services.cursos_service as cursos_logic

from utils.error_handlers import (
    NotFoundError,
    ValidationError
)

from utils.validaciones import (
    validar_body_presente,
    validar_entero,
    validar_string_no_vacio
)


evaluacion_params = [
    "curso_id",
    "tipo_evaluacion_id",
    "titulo",
    "fecha"
]

evaluacion_update_params = [
    "curso_id",
    "tipo_evaluacion_id",
    "titulo",
    "fecha",
    "activo"
]


def obtener_evaluaciones(
    curso_id=None,
    tipo_evaluacion_id=None,
    titulo=None,
    fecha=None,
    activo=None
):

    return db.obtener_evaluaciones(
        curso_id,
        tipo_evaluacion_id,
        titulo,
        fecha,
        activo
    )

def crear_evaluacion(parametros):
    validar_body_presente(parametros)
    for campo in evaluacion_params:
        if campo not in parametros:
            raise ValidationError(
                f"El campo '{campo}' es requerido."
            )

    curso_id = validar_entero(
        parametros["curso_id"],
        "curso_id"
    )
    tipo_evaluacion_id = validar_entero(
        parametros["tipo_evaluacion_id"],
        "tipo_evaluacion_id"
    )
    titulo = validar_string_no_vacio(
        parametros["titulo"],
        "titulo"
    )
    fecha = validar_string_no_vacio(
        parametros["fecha"],
        "fecha"
    )
    descripcion = parametros.get("descripcion")
    return db.crear_evaluacion(
        curso_id,
        tipo_evaluacion_id,
        titulo,
        descripcion,
        fecha
    )

def obtener_evaluacion_por_id(id):
    evaluacion = db.obtener_evaluacion_por_id(id)
    if not evaluacion:
        raise NotFoundError(
            "No se encontró la evaluación"
        )

    return evaluacion

def reemplazar_evaluacion(id, parametros):
    validar_body_presente(parametros)
    for campo in evaluacion_update_params:
        if campo not in parametros:
            raise ValidationError(
                f"El campo '{campo}' es requerido."
            )
        
    curso_id = validar_entero(parametros["curso_id"],"curso_id")
    tipo_evaluacion_id = validar_entero(parametros["tipo_evaluacion_id"],"tipo_evaluacion_id")
    titulo = validar_string_no_vacio(parametros["titulo"],"titulo")
    fecha = validar_string_no_vacio(parametros["fecha"],"fecha")
    activo = parametros["activo"]
    descripcion = parametros.get("descripcion")

    curso = cursos_logic.obtener_curso(curso_id)

    # se tendria que validar que si no es admin, el curso tenga de profesor al usuario ejecutando esta request. 
    # pero tendria que existir la tabla cursos_docentes 

    actualizado = db.reemplazar_evaluacion(
        id,
        curso_id,
        tipo_evaluacion_id,
        titulo,
        descripcion,
        fecha,
        activo
    )
    if not actualizado:
        raise NotFoundError(
            "No se encontró la evaluación"
        )
    return actualizado

def eliminar_evaluacion(id):
    eliminado = db.eliminar_evaluacion(id)
    if not eliminado:
        raise NotFoundError(
            "No se encontró la evaluación"
        )
    return