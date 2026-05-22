from .asistencia_router import asistencia_bp
from .auth_router import auth_bp
from .cursos_router import cursos_bp
from .email_router import email_bp
from .equipos_router import equipos_bp
from .estudiantes_router import estudiantes_bp
from .evaluaciones_router import evaluaciones_bp
from .logs_router import logs_bp
from .materiales_router import materiales_bp
from .reportes_router import reportes_bp
from .usuarios_router import usuarios_bp
from utils import auth_validator as auth

BLUEPRINTS = (
    ("/auth", auth_bp),
    ("/email", email_bp),
    ("/cursos", cursos_bp),
    ("/logs", logs_bp),
    ("/usuarios", usuarios_bp),
    ("/estudiantes", estudiantes_bp),
    ("/evaluaciones", evaluaciones_bp),
    ("/equipos", equipos_bp),
    ("/asistencia", asistencia_bp),
    ("/reportes", reportes_bp),
    ("/materiales", materiales_bp),
)


def register_routes(app):
    app.before_request(auth.validar_token)
    for prefix, bp in BLUEPRINTS:
        app.register_blueprint(bp, url_prefix=prefix)
