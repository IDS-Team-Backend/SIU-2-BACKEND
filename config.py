import os
from dotenv import load_dotenv


load_dotenv()


def _get_env(nombre, required=True, default=None):
    valor = os.getenv(nombre)
    if not valor:
        if default is not None:
            return default
        if required:
            raise RuntimeError(f"Falta la variable de entorno: {nombre}")
        return None
    return valor

ADMIN = "admin"
DOCENTE = "docente"
ALUMNO = "alumno"
AYUDANTE = "ayudante"

ROLES = {
    ADMIN: 1,
    DOCENTE: 2,
    ALUMNO: 3,
    AYUDANTE: 4
}

ESTADOS_CLASE = [ # caso default: ESTADOS_CLASE[0]
    "pendiente",
    "suspendida",
    "en curso",
    "finalizada"
] # CUALQUIER CAMBIO EN LOS ESTADOS, SE DEBE CAMBIAR EN EL SCHEMA.SQL TAMBIEN

EMAIL_CONFIG = {
    "HOST": _get_env("SMTP_HOST", required=False, default=""),
    "PORT": int(_get_env("SMTP_PORT", required=False) or 587),
    "USERNAME": _get_env("SMTP_USERNAME", required=False, default=""),
    "PASSWORD": _get_env("SMTP_PASSWORD", required=False, default=""),
    "SENDER": _get_env("SMTP_SENDER", required=False, default=""),
    "USE_TLS": (_get_env("SMTP_USE_TLS", required=False) or "false").lower() == "true"
}

DOMINIOS_EMAIL_PERMITIDOS = [
    dominio.strip()
    for dominio in os.getenv("DOMINIOS_EMAIL_PERMITIDOS", "fi.uba.ar,gmail.com").split(",")
    if dominio.strip()
]

DB_CONFIG: dict[str, str | int] = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "siu2_db"),
    "port": int(os.getenv("DB_PORT", "3306"))
}
