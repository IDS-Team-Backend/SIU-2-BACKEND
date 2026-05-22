from datetime import timedelta, datetime, timezone
from typing import TypedDict, Dict, Any, Optional
from flask import current_app
import jwt


from utils.error_handlers import UnauthorizedError




class Usuario(TypedDict):
    id: int
    nombre: str
    apellido: str
    rol_id: int
    ... # otros campos extra 

def create_token(usuario: Usuario, perfiles: list) -> str:
    SECRET_KEY = current_app.config["JWT_SECRET_KEY"]
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = current_app.config["JWT_ACCESS_TOKEN_EXPIRES_HOURS"]

    datos_payload = {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "apellido": usuario["apellido"],
        "rol_id": usuario["rol_id"],
        "perfiles": perfiles,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_ACCESS_TOKEN_EXPIRES_HOURS)
    }

    token_jwt = jwt.encode(datos_payload, SECRET_KEY, algorithm="HS256")

    return token_jwt

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    SECRET_KEY = current_app.config["JWT_SECRET_KEY"]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
        
    except jwt.ExpiredSignatureError:
        # el token expiro 
        raise UnauthorizedError("El token ha expirado. Por favor, inicie sesión nuevamente.")
        
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Token invalido o corrupto.")