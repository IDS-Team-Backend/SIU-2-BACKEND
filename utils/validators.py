from datetime import datetime
import os
import re
from dotenv import load_dotenv
from config import DOMINIOS_EMAIL_PERMITIDOS, ESTADOS_CLASE, ROLES
from utils.error_handlers import ValidationError


def validar_fecha(fecha_str):
    from datetime import datetime
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationError("El formato de fecha debe ser YYYY-MM-DD.")
    
def validar_email(email: str):
    if not email:
        return {"valido": False, "mensaje": "El campo email no puede estar vacío."}

    # verifica: 'texto + @ + texto + . + texto'  mediante regex
    patron_formato = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(patron_formato, email):
        return {"valido": False, "mensaje": "El formato del email es incorrecto (ejemplo válido: usuario@dominio.com)."}

    # extrae el dominio
    partes = email.split('@')
    dominio = partes[1].lower()

    # compara el dominio
    if dominio not in DOMINIOS_EMAIL_PERMITIDOS:
        return {"valido": False, "mensaje": f"El dominio '@{dominio}' no está permitido en esta institución."}

    return {"valido": True, "mensaje": ""}

def validar_fecha_hora(fecha_hora_str: str) -> None:
    """
    Valida que la fecha de la clase tenga un formato correcto 
    y que incluya una hora válida (no permite las 00:00).
    Sino lanza ValidationError
    """
    try:
        dt = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # formato estándar ISO con la 'T' en el medio
            dt = datetime.strptime(fecha_hora_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            raise ValidationError("Formato de fecha y hora inválido. Debe ser 'AAAA-MM-DD HH:MM:SS' o 'AAAA-MM-DDTHH:MM:SS'.")

    # si la hora y los minutos son 0 es porque no se mando una hora, solo fecha 
    if dt.hour == 0 and dt.minute == 0:
        raise ValidationError("Debe especificar una hora válida para la clase. No se permiten las 00:00 hs.")
    
    if dt < datetime.now():
        raise ValidationError("La fecha y hora de la clase no puede ser en el pasado.")
    
def validar_rango_fecha(fecha_hora_inicio: str, fecha_hora_fin: str) -> None:
    """
    Valida que un rango de datetimes (fecha_hora_inicio y fecha_hora_fin) cumpla con las siguientes reglas:
    1) fecha_hora_fin debe ser estrictamente mayor a fecha_hora_inicio
    2) Ambas fechas deben pertenecer al mismo día calendario (no se permiten clases de corrido entre días distintos)
    """
    formato = "%Y-%m-%d %H:%M:%S"
        
    # 1. Convertimos los strings a objetos datetime
    dt_inicio = datetime.strptime(fecha_hora_inicio, formato)
    dt_fin = datetime.strptime(fecha_hora_fin, formato)

    # fecha_hora_fin debe ser mayor a fecha_hora_inicio
    if dt_fin <= dt_inicio:
        raise ValidationError("La fecha y hora de fin debe ser posterior a la de comienzo.")

    # ambas fechas deben ser del mismo dia 
    if dt_inicio.date() != dt_fin.date():
        raise ValidationError("La fecha y hora de inicio y fin deben pertenecer al mismo día calendario. No se permiten clases de corrido entre días distintos.")

def id_rol_a_nombre(rol_id):
    for nombre, id in ROLES.items():
        if id == rol_id:
            return nombre
    return None

def es_estado_clase_valido(estado: str) -> bool:
    """Valida si un estado de clase enviado por el cliente es correcto."""
    return estado in ESTADOS_CLASE

def es_rol_valido(rol_id: int) -> bool:
    """Valida si un rol_id corresponde a un rol existente."""
    return rol_id in ROLES.values()