import os
from dotenv import load_dotenv


load_dotenv()


def _get_env(nombre, required=True):
    valor = os.getenv(nombre)
    if not valor and required:
        raise RuntimeError(f"Falta la variable de entorno: {nombre}")
    return valor

ROLES = {
    "admin": 1,
    "docente": 2,
    "alumno": 3,
    "ayudante": 4
}

ESTADOS_CLASE = [ # caso default: ESTADOS_CLASE[0]
    "pendiente",
    "suspendida",
    "en curso",
    "finalizada"
] # CUALQUIER CAMBIO EN LOS ESTADOS, SE DEBE CAMBIAR EN EL SCHEMA.SQL TAMBIEN

EMAIL_CONFIG = {
    "HOST": _get_env("SMTP_HOST"),
    "PORT": int(_get_env("SMTP_PORT") or "587"),
    "USERNAME": _get_env("SMTP_USERNAME"),
    "PASSWORD": _get_env("SMTP_PASSWORD"),
    "SENDER": _get_env("SMTP_SENDER"),
    "USE_TLS": (_get_env("SMTP_USE_TLS") or "false").lower() == "true"
}

DOMINIOS_EMAIL_PERMITIDOS = [  # en caso de que solo se permitan emails institucionales 
    "fiuba.edu.ar",
    "alumnos.fiuba.edu.ar"
]

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "siu2_db"),
    "port": int(os.getenv("DB_PORT", 3306))
}
