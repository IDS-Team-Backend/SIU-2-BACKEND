from datetime import timedelta
import os
from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager

from routes import register_routes
import utils.error_handlers as error_handlers
# import utils.middleware_hateoas as middleware

app = Flask(__name__)

# middleware.start_hateoas(app)
error_handlers.start(app)

register_routes(app)


load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("CRÍTICO: La variable JWT_SECRET no está configurada en el entorno.")

app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY

horas_expiracion = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 2))
app.config["JWT_ACCESS_TOKEN_EXPIRES_HOURS"] = horas_expiracion

jwt = JWTManager(app)

import sys
if __name__ == "__main__":
    port = 5000  # default

    if len(sys.argv) > 1: # si se pasa un argumento al ejecutar 'python app.py {numero_puerto}' se ejecuta en el puerto indicado 
        port = int(sys.argv[1])

    app.run(port=port, debug=True)

