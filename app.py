from flask import Flask

from routes.asistencia_router import asistencia_bp
from routes.auth_router import auth_bp
from routes.alumnos_router import alumnos_bp
from routes.equipos_router import equipos_bp
from routes.evaluaciones_router import evaluaciones_bp
from routes.logs_router import logs_bp
from routes.materiales_router import materiales_bp
from routes.reportes_router import reportes_bp
import utils.error_handlers as error_handlers
# import utils.middleware_hateoas as middleware

app = Flask(__name__)

# middleware.start_hateoas(app)
error_handlers.start(app)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(logs_bp, url_prefix="/logs")
app.register_blueprint(alumnos_bp, url_prefix="/alumnos")
app.register_blueprint(evaluaciones_bp, url_prefix="/evaluaciones")
app.register_blueprint(equipos_bp, url_prefix="/equipos")
app.register_blueprint(asistencia_bp, url_prefix="/asistencia")
app.register_blueprint(reportes_bp, url_prefix="/reportes")
app.register_blueprint(materiales_bp, url_prefix="/materiales")

import sys
if __name__ == "__main__":
    port = 5000  # default

    if len(sys.argv) > 1: # si se pasa un argumento al ejecutar 'python app.py {numero_puerto}' se ejecuta en el puerto indicado 
        port = int(sys.argv[1])

    app.run(port=port, debug=True)

