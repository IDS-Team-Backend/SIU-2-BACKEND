from .materias_router import materias_bp
from .asistencia_router import asistencia_bp
from .auth_router import auth_public_bp, auth_private_bp
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
from .estudiante_curso_router import estudiante_curso_bp

from utils import auth_validator as auth
from .equipo_integrantes_router import equipo_integrantes_bp
from .notas_router import notas_bp
from .clases_router import clases_bp

BLUEPRINTS_PUBLICOS = [
    ("/auth",       auth_public_bp),
    ("/materiales", materiales_bp),
]

BLUEPRINTS_PRIVADOS = [
    ("/auth",              auth_private_bp),
    ("/email",             email_bp),
    ("/cursos",            cursos_bp),
    ("/logs",              logs_bp),
    ("/usuarios",          usuarios_bp),
    ("/estudiantes",       estudiantes_bp),
    ("/profesores",        profesores_bp),
    ("/evaluaciones",      evaluaciones_bp),
    ("/equipos",           equipos_bp),
    ("/asistencia",        asistencia_bp),
    ("/reportes",          reportes_bp),
    ("/materias",          materias_bp),
    ("/estudiante_curso",  estudiante_curso_bp),
    ("/equipo_integrantes", equipo_integrantes_bp),
    ("/notas",             notas_bp),
    ("/clases",            clases_bp),
]


def register_routes(app):
    for prefix, bp in BLUEPRINTS_PUBLICOS:
        app.register_blueprint(bp, url_prefix=prefix)

    for prefix, bp in BLUEPRINTS_PRIVADOS:
        bp.before_request(auth.validar_token)
        app.register_blueprint(bp, url_prefix=prefix)
