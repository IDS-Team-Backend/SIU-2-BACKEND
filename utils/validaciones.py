import logging
import re
from datetime import datetime, date

from config import DOMINIOS_EMAIL_PERMITIDOS
from utils.error_handlers import ValidationError


logger = logging.getLogger(__name__)


_PATRON_EMAIL = r'^[\w\.-]+@[\w\.-]+\.\w+$'
_FORMATOS_FECHA_HORA = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S")


def validar_body_presente(body):
    if not isinstance(body, dict):
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")


def validar_campos_permitidos(body, permitidos):
    extras = set(body.keys()) - set(permitidos)
    if extras:
        raise ValidationError(
            f"Los campos {sorted(extras)} no son válidos. "
            f"Campos permitidos: {', '.join(permitidos)}."
        )


def validar_entero(numero, nombre="numero"):
    try:
        return int(str(numero))
    except (ValueError, TypeError):
        logger.warning(f"Valor numérico inválido: '{numero}' no puede convertirse a entero")
        raise ValidationError(
            f"El valor de '{nombre}' debe ser un número entero. Se recibió: {numero!r}"
        )


def validar_minimo(valor, minimo, nombre):
    if valor < minimo:
        raise ValidationError(
            f"El campo '{nombre}' debe ser mayor o igual a {minimo}. Se recibió: {valor}"
        )
    return valor


def validar_maximo(valor, maximo, nombre):
    if valor > maximo:
        raise ValidationError(
            f"El campo '{nombre}' debe ser menor o igual a {maximo}. Se recibió: {valor}"
        )
    return valor


def validar_string_no_vacio(valor, nombre):
    if valor is None or not str(valor).strip():
        raise ValidationError(f"El campo '{nombre}' es obligatorio y no puede estar vacío.")
    return str(valor).strip()


def validar_largo_string(valor, minimo, maximo, nombre):
    if len(valor) < minimo:
        raise ValidationError(
            f"El campo '{nombre}' debe tener al menos {minimo} caracteres."
        )
    if len(valor) > maximo:
        raise ValidationError(
            f"El campo '{nombre}' debe tener como máximo {maximo} caracteres."
        )
    return valor


def validar_booleano(valor, nombre):
    if not isinstance(valor, bool):
        raise ValidationError(f"El campo '{nombre}' debe ser booleano. Se recibió: {valor!r}")
    return valor


def validar_fecha(valor, nombre, permitir_futura=True):
    if valor is None or not str(valor).strip():
        raise ValidationError(f"El campo '{nombre}' es obligatorio y no puede estar vacío.")
    try:
        fecha = datetime.strptime(str(valor).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError(
            f"El campo '{nombre}' debe tener formato YYYY-MM-DD. Se recibió: {valor!r}"
        )
    if not permitir_futura and fecha > date.today():
        raise ValidationError(
            f"El campo '{nombre}' no puede ser una fecha futura. Se recibió: {valor}"
        )
    return fecha.isoformat()


def _parse_fecha_hora(valor, nombre):
    valor_str = str(valor).strip() if valor is not None else ""
    if not valor_str:
        raise ValidationError(f"El campo '{nombre}' es obligatorio y no puede estar vacío.")
    for formato in _FORMATOS_FECHA_HORA:
        try:
            return datetime.strptime(valor_str, formato)
        except ValueError:
            continue
    raise ValidationError(
        f"El campo '{nombre}' debe tener formato 'AAAA-MM-DD HH:MM:SS' o 'AAAA-MM-DDTHH:MM:SS'."
    )


def validar_fecha_hora(valor, nombre, permitir_pasada=False):
    dt = _parse_fecha_hora(valor, nombre)
    if dt.hour == 0 and dt.minute == 0:
        raise ValidationError(
            f"Debe especificar una hora válida para '{nombre}'. No se permiten las 00:00 hs."
        )
    if not permitir_pasada and dt < datetime.now():
        raise ValidationError(f"El campo '{nombre}' no puede ser en el pasado.")
    return dt


def validar_rango_fecha(inicio, fin, nombre_inicio="inicio", nombre_fin="fin", mismo_dia=True):
    dt_inicio = _parse_fecha_hora(inicio, nombre_inicio)
    dt_fin = _parse_fecha_hora(fin, nombre_fin)
    if dt_fin <= dt_inicio:
        raise ValidationError(
            f"La fecha y hora de '{nombre_fin}' debe ser posterior a la de '{nombre_inicio}'."
        )
    if mismo_dia and dt_inicio.date() != dt_fin.date():
        raise ValidationError(
            f"Las fechas de '{nombre_inicio}' y '{nombre_fin}' deben pertenecer al mismo día calendario."
        )


def validar_email(valor, nombre="email"):
    if valor is None or not str(valor).strip():
        raise ValidationError(f"El campo '{nombre}' no puede estar vacío.")
    valor = str(valor).strip()
    if not re.match(_PATRON_EMAIL, valor):
        raise ValidationError(
            f"El formato del campo '{nombre}' es incorrecto (ejemplo válido: usuario@dominio.com)."
        )
    dominio = valor.split('@')[1].lower()
    if dominio not in DOMINIOS_EMAIL_PERMITIDOS:
        raise ValidationError(f"El dominio '@{dominio}' no está permitido en esta institución.")
    return valor


def validar_valor_en(valor, opciones, nombre):
    if valor not in opciones:
        raise ValidationError(
            f"El valor de '{nombre}' es inválido. Valores válidos: {', '.join(map(str, opciones))}."
        )
    return valor
