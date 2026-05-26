import logging

from constants import (
    ERROR_CODE_INVALID_BODY,
    ERROR_CODE_INVALID_TYPE,
    ERROR_CODE_INVALID_MIN_VALUE,
    ERROR_CODE_INVALID_MAX_VALUE,
)


logger = logging.getLogger(__name__)


def construir_error_api(code, message, description, level="error"):
    return {
        "errors": [{
            "code": code,
            "message": message,
            "level": level,
            "description": description,
        }]
    }


def validar_body_presente(body):
    if body is None:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message="Cuerpo de la solicitud inválido",
            description="El cuerpo debe ser un JSON válido con Content-Type application/json",
        ))


def validar_entero(numero, nombre="numero"):
    try:
        return int(str(numero))
    except (ValueError, TypeError):
        logger.warning(f"Valor numérico inválido: '{numero}' no puede convertirse a entero")
        raise ValueError(construir_error_api(
            code=f"invalid.{nombre}.format",
            message=f"Formato de '{nombre}' inválido",
            description=f"El valor '{numero}' no puede convertirse a un número entero",
        ))


def validar_minimo(valor, minimo, nombre):
    if valor < minimo:
        logger.warning(f"Valor por debajo del mínimo: '{nombre}' es {valor}, mínimo esperado {minimo}")
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MIN_VALUE,
            message="Valor por debajo del mínimo permitido",
            description=f"El parámetro '{nombre}' debe ser mayor o igual a {minimo}. Se recibió: {valor}",
        ))
    return valor


def validar_maximo(valor, maximo, nombre):
    if valor > maximo:
        logger.warning(f"Valor por encima del máximo: '{nombre}' es {valor}, máximo esperado {maximo}")
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MAX_VALUE,
            message="Valor por encima del máximo permitido",
            description=f"El parámetro '{nombre}' debe ser menor o igual a {maximo}. Se recibió: {valor}",
        ))
    return valor


def validar_string_no_vacio(valor, nombre):
    if valor is None or not str(valor).strip():
        raise ValueError(construir_error_api(
            code=f"required.{nombre}",
            message=f"Campo requerido: '{nombre}'",
            description=f"El campo '{nombre}' es obligatorio y no puede estar vacío",
        ))
    return str(valor).strip()


def validar_largo_string(valor, minimo, maximo, nombre):
    if len(valor) < minimo:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MIN_VALUE,
            message=f"Longitud mínima no alcanzada en '{nombre}'",
            description=f"El campo '{nombre}' debe tener al menos {minimo} caracteres",
        ))
    if len(valor) > maximo:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MAX_VALUE,
            message=f"Longitud máxima superada en '{nombre}'",
            description=f"El campo '{nombre}' debe tener como máximo {maximo} caracteres",
        ))
    return valor


def validar_booleano(valor, nombre):
    if not isinstance(valor, bool):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_TYPE,
            message=f"El campo '{nombre}' debe ser booleano",
            description=f"Se recibió: {valor!r}",
        ))
    return valor
