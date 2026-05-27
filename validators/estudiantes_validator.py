from datetime import datetime

from utils import validaciones
from utils.error_handlers import ValidationError


ANIO_INGRESO_MIN = 1900
CAMPOS_PATCH_PERMITIDOS = ("padron", "carrera", "anio_ingreso", "activo")


def _anio_ingreso_max():
    return datetime.now().year + 1


def _validar_padron(body, errores, resultado):
    try:
        padron = validaciones.validar_entero(body.get("padron"), "padron")
        resultado["padron"] = validaciones.validar_minimo(padron, 1, "padron")
    except ValidationError as e:
        errores.append(str(e))


def _validar_carrera(body, errores, resultado):
    try:
        carrera = validaciones.validar_string_no_vacio(body.get("carrera"), "carrera")
        resultado["carrera"] = validaciones.validar_largo_string(carrera, 1, 150, "carrera")
    except ValidationError as e:
        errores.append(str(e))


def _validar_anio_ingreso(body, errores, resultado):
    try:
        anio = validaciones.validar_entero(body.get("anio_ingreso"), "anio_ingreso")
        anio = validaciones.validar_minimo(anio, ANIO_INGRESO_MIN, "anio_ingreso")
        resultado["anio_ingreso"] = validaciones.validar_maximo(anio, _anio_ingreso_max(), "anio_ingreso")
    except ValidationError as e:
        errores.append(str(e))


def _validar_activo(body, errores, resultado):
    try:
        resultado["activo"] = validaciones.validar_booleano(body.get("activo"), "activo")
    except ValidationError as e:
        errores.append(str(e))


def _validar_usuario_id(body, errores, resultado):
    try:
        usuario_id = validaciones.validar_entero(body.get("usuario_id"), "usuario_id")
        resultado["usuario_id"] = validaciones.validar_minimo(usuario_id, 1, "usuario_id")
    except ValidationError as e:
        errores.append(str(e))


def validar_body_crear_estudiante(body):
    validaciones.validar_body_presente(body)

    errores = []
    resultado = {}

    _validar_usuario_id(body, errores, resultado)
    _validar_padron(body, errores, resultado)
    _validar_carrera(body, errores, resultado)
    _validar_anio_ingreso(body, errores, resultado)

    if errores:
        raise ValidationError(errores)

    return resultado


def validar_body_reemplazar_estudiante(body):
    validaciones.validar_body_presente(body)

    errores = []
    resultado = {}

    _validar_padron(body, errores, resultado)
    _validar_carrera(body, errores, resultado)
    _validar_anio_ingreso(body, errores, resultado)
    _validar_activo(body, errores, resultado)

    if errores:
        raise ValidationError(errores)

    return resultado


def validar_body_modificar_estudiante(body):
    validaciones.validar_body_presente(body)
    validaciones.validar_campos_permitidos(body, CAMPOS_PATCH_PERMITIDOS)

    errores = []
    resultado = {}

    if "padron" in body:
        _validar_padron(body, errores, resultado)
    if "carrera" in body:
        _validar_carrera(body, errores, resultado)
    if "anio_ingreso" in body:
        _validar_anio_ingreso(body, errores, resultado)
    if "activo" in body:
        _validar_activo(body, errores, resultado)

    if errores:
        raise ValidationError(errores)

    if not resultado:
        raise ValidationError("Debe enviar al menos un campo a modificar.")

    return resultado
