from modules.asistencia.asistencia_route import asistencia_bp
from modules.auth.auth_route import auth_public_bp, auth_private_bp, password_bp, password_private_bp
from modules.clases.clases_route import clases_bp
from modules.curso_docentes.curso_docentes_route import curso_docentes_bp
from modules.cursos.cursos_route import cursos_bp, cursos_public_bp
from modules.email.email_route import email_bp
from modules.entregas.entregas_route import entregas_bp
from modules.equipo_integrantes.equipo_integrantes_route import equipo_integrantes_bp
from modules.equipos.equipos_route import equipos_bp
from modules.estudiante_curso.estudiante_curso_route import estudiante_curso_bp
from modules.estudiantes.estudiantes_route import estudiantes_bp
from modules.evaluaciones.evaluaciones_route import evaluaciones_bp
from modules.logs.logs_route import logs_bp
from modules.materiales.materiales_route import materiales_bp, materiales_public_bp
from modules.materias.materias_route import materias_bp
from modules.notas.notas_route import notas_bp
from modules.profesores.profesores_route import profesores_bp
from modules.reportes.reportes_route import reportes_bp
from modules.tipos_evaluacion.tipos_evaluacion_route import tipos_evaluacion_bp
from modules.usuarios.usuarios_route import usuarios_bp

from utils import auth_validator as auth

BLUEPRINTS_PUBLICOS = [
    ("/auth",            auth_public_bp),
    ("/materiales",      materiales_public_bp),
    ("/password",        password_bp),
    ("/cursos-publico",  cursos_public_bp),
]

BLUEPRINTS_PRIVADOS = [
    ("/auth",               auth_private_bp),
    ("/password",           password_private_bp),
    ("/materiales",         materiales_bp),
    ("/email",              email_bp),
    ("/cursos",             cursos_bp),
    ("/logs",               logs_bp),
    ("/usuarios",           usuarios_bp),
    ("/estudiantes",        estudiantes_bp),
    ("/profesores",         profesores_bp),
    ("/evaluaciones",       evaluaciones_bp),
    ("/equipos",            equipos_bp),
    ("/asistencia",         asistencia_bp),
    ("/reportes",           reportes_bp),
    ("/materias",           materias_bp),
    ("/estudiante_curso",   estudiante_curso_bp),
    ("/curso_docentes",     curso_docentes_bp),
    ("/equipo_integrantes", equipo_integrantes_bp),
    ("/notas",              notas_bp),
    ("/entregas",           entregas_bp),
    ("/clases",             clases_bp),
    ("/tipos_evaluacion",   tipos_evaluacion_bp),
]


def register_routes(app):
    for prefix, bp in BLUEPRINTS_PUBLICOS:
        app.register_blueprint(bp, url_prefix=prefix)

    for prefix, bp in BLUEPRINTS_PRIVADOS:
        bp.before_request(auth.validar_token)
        app.register_blueprint(bp, url_prefix=prefix)
