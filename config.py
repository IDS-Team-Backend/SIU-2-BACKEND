import os
from dotenv import load_dotenv


load_dotenv()


def _get_env(nombre, required=True):
    valor = os.getenv(nombre)
    if not valor and required:
        raise RuntimeError(f"Falta la variable de entorno: {nombre}")
    return valor


class EmailConfig:
    HOST     = _get_env("SMTP_HOST")
    PORT     = int(_get_env("SMTP_PORT"))
    USERNAME = _get_env("SMTP_USERNAME")
    PASSWORD = _get_env("SMTP_PASSWORD")
    SENDER   = _get_env("SMTP_SENDER")
    USE_TLS  = _get_env("SMTP_USE_TLS").lower() == "true"


# class DatabaseConfig:
#     HOST     = _get_env("DB_HOST")
#     PORT     = int(_get_env("DB_PORT"))
#     USER     = _get_env("DB_USER")
#     PASSWORD = _get_env("DB_PASSWORD")
#     NAME     = _get_env("DB_NAME")
