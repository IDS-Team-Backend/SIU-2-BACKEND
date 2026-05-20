from typing import TypedDict, Dict, Any, Optional
import datetime

from flask_jwt_extended import create_access_token
import jwt


class Usuario(TypedDict):
    id: int
    nombre: str
    apellido: str
    rol_id: int
    ... # otros campos extra 

def create_token(usuario: Usuario) -> str:
    identity_usuario = str(usuario["id"])

    datos_payload = {
        "nombre": usuario["nombre"],
        "apellido": usuario["apellido"],
        "rol_id": usuario["rol_id"]
    }

    token_jwt = create_access_token(
        identity=identity_usuario, 
        additional_claims=datos_payload
    )

    return token_jwt

# el token se valida solo al usar el decorador @jwt_required() en las rutas