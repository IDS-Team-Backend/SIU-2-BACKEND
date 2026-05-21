import os
import re
from dotenv import load_dotenv
from utils.error_handlers import ValidationError


def validar_fecha(fecha_str):
    from datetime import datetime
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationError("El formato de fecha debe ser YYYY-MM-DD.")
    
load_dotenv()

dominios_raw = os.getenv("DOMINIOS_EMAIL_PERMITIDOS", "gmail.com")
DOMINIOS_PERMITIDOS = [dominio.strip().lower() for dominio in dominios_raw.split(',')] # pasar del formato .env a una lista de python

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

    print(dominio, DOMINIOS_PERMITIDOS, flush=True)
    # compara el dominio
    if dominio not in DOMINIOS_PERMITIDOS:
        return {"valido": False, "mensaje": f"El dominio '@{dominio}' no está permitido en esta institución."}

    return {"valido": True, "mensaje": ""}