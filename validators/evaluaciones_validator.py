from utils import validaciones
from utils.error_handlers import ValidationError


CAMPOS_OBLIGATORIOS_CREAR = ("curso_id", "tipo_evaluacion_id", "titulo", "fecha")
CAMPOS_OPCIONALES_CREAR = ("descripcion",)
CAMPOS_PERMITIDOS_CREAR = CAMPOS_OBLIGATORIOS_CREAR + CAMPOS_OPCIONALES_CREAR

CAMPOS_OBLIGATORIOS_REEMPLAZAR = ("curso_id", "tipo_evaluacion_id", "titulo", "fecha", "activo")
CAMPOS_OPCIONALES_REEMPLAZAR = ("descripcion",)
CAMPOS_PERMITIDOS_REEMPLAZAR = CAMPOS_OBLIGATORIOS_REEMPLAZAR + CAMPOS_OPCIONALES_REEMPLAZAR


def _validar_curso_id(body, errores, resultado):
    try:
        curso = validaciones.validar_entero(body.get("curso_id"), "curso_id")
        resultado["curso_id"] = validaciones.validar_minimo(curso, 1, "curso_id")
    except ValidationError as e:
        errores.append(str(e))


def _validar_tipo_evaluacion_id(body, errores, resultado):
    try:
        tipo = validaciones.validar_entero(body.get("tipo_evaluacion_id"), "tipo_evaluacion_id")
        resultado["tipo_evaluacion_id"] = validaciones.validar_minimo(tipo, 1, "tipo_evaluacion_id")
    except ValidationError as e:
        errores.append(str(e))


def _validar_titulo(body, errores, resultado):
    try:
        titulo = validaciones.validar_string_no_vacio(body.get("titulo"), "titulo")
        resultado["titulo"] = validaciones.validar_largo_string(titulo, 1, 150, "titulo")
    except ValidationError as e:
        errores.append(str(e))


def _validar_fecha(body, errores, resultado):
    try:
        resultado["fecha"] = validaciones.validar_string_no_vacio(body.get("fecha"), "fecha")
    except ValidationError as e:
        errores.append(str(e))


def _validar_activo(body, errores, resultado):
    try:
        resultado["activo"] = validaciones.validar_booleano(body.get("activo"), "activo")
    except ValidationError as e:
        errores.append(str(e))


def validar_body_crear_evaluacion(body):
    validaciones.validar_body_presente(body)
    validaciones.validar_campos_permitidos(body, CAMPOS_PERMITIDOS_CREAR)

    errores = []
    resultado = {}

    _validar_curso_id(body, errores, resultado)
    _validar_tipo_evaluacion_id(body, errores, resultado)
    _validar_titulo(body, errores, resultado)
    _validar_fecha(body, errores, resultado)

    if errores:
        raise ValidationError(errores)

    resultado["descripcion"] = body.get("descripcion")
    return resultado


def validar_body_reemplazar_evaluacion(body):
    validaciones.validar_body_presente(body)
    validaciones.validar_campos_permitidos(body, CAMPOS_PERMITIDOS_REEMPLAZAR)

    errores = []
    resultado = {}

    _validar_curso_id(body, errores, resultado)
    _validar_tipo_evaluacion_id(body, errores, resultado)
    _validar_titulo(body, errores, resultado)
    _validar_fecha(body, errores, resultado)
    _validar_activo(body, errores, resultado)

    if errores:
        raise ValidationError(errores)

    resultado["descripcion"] = body.get("descripcion")
    return resultado
