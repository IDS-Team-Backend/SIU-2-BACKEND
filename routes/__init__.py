from .materias_router import materias_bp
from .asistencia_router import asistencia_bp
from .auth_router import auth_bp
from .cursos_router import cursos_bp
from .email_router import email_bp
from .equipos_router import equipos_bp
from .estudiantes_router import estudiantes_bp
from .profesores_router import profesores_bp
from .evaluaciones_router import evaluaciones_bp
from .logs_router import logs_bp
from .materiales_router import materiales_bp
from .reportes_router import reportes_bp
from .usuarios_router import usuarios_bp
from .curso_usuarios_router import curso_usuarios_bp

from utils import auth_validator as auth
from .equipo_integrantes_router import equipo_integrantes_bp
from .notas_router import notas_bp
from .clases_router import clases_bp

BLUEPRINTS = (
    ("/auth", auth_bp),
    ("/email", email_bp),
    ("/cursos", cursos_bp),
    ("/logs", logs_bp),
    ("/usuarios", usuarios_bp),
    ("/estudiantes", estudiantes_bp),
    ("/profesores", profesores_bp),
    ("/evaluaciones", evaluaciones_bp),
    ("/equipos", equipos_bp),
    ("/asistencia", asistencia_bp),
    ("/reportes", reportes_bp),
    ("/materiales", materiales_bp),
    ("/curso_usuarios", curso_usuarios_bp),
    ("/equipo_integrantes", equipo_integrantes_bp),
    ("/materias", materias_bp),
    ("/notas", notas_bp),
    ("/clases", clases_bp),
)

RUTAS_NO_PROTEGIDAS = (
    "/auth",
    "/materiales"
)


def register_routes(app):
    for prefix, bp in BLUEPRINTS:

        if prefix not in RUTAS_NO_PROTEGIDAS:
            bp.before_request(auth.validar_token)  # proteger rutas con autenticacion

        app.register_blueprint(bp, url_prefix=prefix)
