from modules.cursada.asistencia.asistencia_route import asistencia_bp
from modules.personas.auth.auth_route import auth_public_bp, auth_private_bp, password_bp, password_private_bp
from modules.cursada.clases.clases_route import clases_bp
from modules.cursada.curso_docentes.curso_docentes_route import curso_docentes_bp
from modules.cursada.cursos.cursos_route import cursos_bp, cursos_public_bp
from modules.sistema.email.email_route import email_bp
from modules.evaluacion.entregas.entregas_route import entregas_bp
from modules.evaluacion.equipo_integrantes.equipo_integrantes_route import equipo_integrantes_bp
from modules.evaluacion.equipos.equipos_route import equipos_bp
from modules.cursada.estudiante_curso.estudiante_curso_route import estudiante_curso_bp
from modules.personas.estudiantes.estudiantes_route import estudiantes_bp
from modules.evaluacion.evaluaciones.evaluaciones_route import evaluaciones_bp
from modules.sistema.logs.logs_route import logs_bp
from modules.cursada.materiales.materiales_route import materiales_bp, materiales_public_bp
from modules.cursada.materias.materias_route import materias_bp
from modules.evaluacion.notas.notas_route import notas_bp
from modules.personas.profesores.profesores_route import profesores_bp
from modules.sistema.reportes.reportes_route import reportes_bp
from modules.evaluacion.tipos_evaluacion.tipos_evaluacion_route import tipos_evaluacion_bp
from modules.personas.usuarios.usuarios_route import usuarios_bp

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
