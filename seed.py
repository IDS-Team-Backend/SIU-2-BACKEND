import json

from db import execute_query
from werkzeug.security import generate_password_hash


def seed_materias():
    materias = [
        ("Algoritmos y Programación", "75.40"),
        ("Base de Datos", "75.06"),
        ("Organización de Datos", "75.41"),
    ]

    query = """
    INSERT IGNORE INTO materias(nombre, codigo)
    VALUES (%s, %s)
    """

    for materia in materias:
        execute_query(query, materia, modifica_db=True)


def seed_tipos_evaluacion():
    tipos = [
        ("Parcial", False),
        ("TP", True),
        ("Final", False),
    ]

    query = """
    INSERT IGNORE INTO tipos_evaluacion(nombre, es_grupal)
    VALUES (%s, %s)
    """

    for tipo in tipos:
        execute_query(query, tipo, modifica_db=True)


def seed_usuarios():
    password = generate_password_hash("123456")

    usuarios = [
        # sistema y docente
        ("admin",      "Del Sistema", "admin@fi.uba.ar",        47000000, password, True),
        ("Juan Carlos","Perez",       "jperez@fi.uba.ar",       47000001, password, False),
        # integrantes del grupo (primeros)
        ("Nicolas",    "Martinez",    "nmartinez@fi.uba.ar",    44100001, password, False),
        ("Franco",     "Dimeola",     "fdimeola@fi.uba.ar",     44100002, password, False),
        ("Federico",   "Folgar",      "ffolgar@fi.uba.ar",      44100003, password, False),
        ("Joaquin",    "Fernandez",   "jfernandez@fi.uba.ar",   44100004, password, False),
        ("Tomas",      "Vargas",      "tvargas@fi.uba.ar",      44215876, password, False),
        # resto de alumnos
        ("Sofia",      "Ramirez",     "sramirez@fi.uba.ar",     47000004, password, False),
        ("Camila",     "Lopez",       "clopez@fi.uba.ar",       47000005, password, False),
        ("Valentina",  "Torres",      "vtorres@fi.uba.ar",      47000006, password, False),
        ("Agustin",    "Diaz",        "adiaz@fi.uba.ar",        47000007, password, False),
        ("Florencia",  "Sanchez",     "fsanchez@fi.uba.ar",     47000008, password, False),
        ("Matias",     "Morales",     "mmorales@fi.uba.ar",     47000009, password, False),
        ("Julieta",    "Gutierrez",   "jgutierrez@fi.uba.ar",   47000010, password, False),
        ("Santiago",   "Romero",      "sromero@fi.uba.ar",      47000011, password, False),
        ("Micaela",    "Alvarez",     "malvarez@fi.uba.ar",     47000012, password, False),
        ("Lucia",      "Castro",      "lcastro@fi.uba.ar",      47000013, password, False),
        ("Ezequiel",   "Ortiz",       "eortiz@fi.uba.ar",       47000014, password, False),
        ("Martina",    "Ruiz",        "mruiz@fi.uba.ar",        47000015, password, False),
        ("Ignacio",    "Jimenez",     "ijimenez@fi.uba.ar",     47000016, password, False),
        ("Rocio",      "Herrera",     "rherrera@fi.uba.ar",     47000017, password, False),
        ("Leandro",    "Medina",      "lmedina@fi.uba.ar",      47000018, password, False),
        ("Pilar",      "Silva",       "psilva@fi.uba.ar",       47000019, password, False),
        ("Facundo",    "Molina",      "fmolina@fi.uba.ar",      47000020, password, False),
        ("Carla",      "Mendez",      "cmendez@fi.uba.ar",      47000021, password, False),
        ("Maximo",     "Delgado",     "mdelgado@fi.uba.ar",     47000022, password, False),
        ("Bianca",     "Reyes",       "breyes@fi.uba.ar",       47000023, password, False),
        ("Rodrigo",    "Soto",        "rsoto@fi.uba.ar",        47000024, password, False),
        ("Azul",       "Moran",       "amoran@fi.uba.ar",       47000025, password, False),
        ("Julian",     "Vega",        "jvega@fi.uba.ar",        47000026, password, False),
        ("Nadia",      "Pereyra",     "npereyra@fi.uba.ar",     47000027, password, False),
        ("Bruno",      "Navarro",     "bnavarro@fi.uba.ar",     47000028, password, False),
        ("Celeste",    "Ibarra",      "cibarra@fi.uba.ar",      47000029, password, False),
        ("Gino",       "Dominguez",   "gdominguez@fi.uba.ar",   47000030, password, False),
        ("Aldana",     "Ferreyra",    "aferreyra@fi.uba.ar",    47000031, password, False),
        ("Thiago",     "Cabrera",     "tcabrera@fi.uba.ar",     47000032, password, False),
        ("Belen",      "Aguilar",     "baguilar@fi.uba.ar",     47000033, password, False),
        ("mateo", "Martinez", "mateo@fi.uba.ar", 47000004, password, False),
        ("thiago", "Martinez", "thiago@fi.uba.ar", 47000005, password, False),
    ]

    query = """
    INSERT IGNORE INTO usuarios(
        nombre,
        apellido,
        email,
        dni,
        password_hash,
        es_admin
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    for usuario in usuarios:
        execute_query(query, usuario, modifica_db=True)

def seed_estudiantes():
    C = ["Ingeniería en Informática", "Licenciatura en Análisis de Sistemas", "Ingeniería Civil", "Ingeniería Electrónica"]
    # (usuario_id, padron, carrera, anio_ingreso)
    # usuario_ids 3-7: integrantes del grupo; 8+ alumnos varios
    estudiantes = [
        (3, 100002, "Ingeniería en Informática", 2024),
        (4, 100003, "Ingeniería en Informática", 2024),
    ]

    query = """
    INSERT IGNORE INTO estudiantes(
        usuario_id,
        padron,
        carrera,
        anio_ingreso
    )
    VALUES (%s, %s, %s, %s)
    """

    for estudiante in estudiantes:
        execute_query(query, estudiante, modifica_db=True)


def seed_profesores():
    profesores = [
        (2, 500001, "Ingeniero en Informática", "Informática", "2018-03-01"),
        (5, 500002, "Licenciado en Sistemas", "Informática", "2020-04-15"),   # ID 2 (Ayudante)
        (6, 500003, "Analista de Sistemas", "Informática", "2022-08-10"),     # ID 3 (JTP)
    ]

    query = """
    INSERT IGNORE INTO profesores(
        usuario_id,
        legajo,
        titulo,
        departamento,
        fecha_ingreso
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    for profesor in profesores:
        execute_query(query, profesor, modifica_db=True)


def seed_cursos():
    cursos = [
        (1, "Curso A", 2026, 1),
        (2, "Curso B", 2026, 1),
    ]

    query = """
    INSERT IGNORE INTO cursos(
        materia_id,
        nombre,
        anio,
        cuatrimestre
    )
    VALUES (%s, %s, %s, %s)
    """

    for curso in cursos:
        execute_query(query, curso, modifica_db=True)

def seed_curso_docentes():
    # (curso_id, docente_id, nombre)
    # Solo usamos curso_id 1 y 2, y docente_id 1 (que son los que existen)
    curso_docentes = [
        (1, 1, "titular"), 
        (2, 1, "titular"),
        (1, 2, "jefe_tp"), 
        (1, 3, "ayudante") 
    ]

    query = """
    INSERT IGNORE INTO curso_docentes(
        curso_id,
        docente_id,
        nombre
    )
    VALUES (%s, %s, %s)
    """

    for cd in curso_docentes:
        execute_query(query, cd, modifica_db=True)


def seed_inscripciones():
    # todos los estudiantes inscriptos en curso_id=1
    inscripciones = [(1, i) for i in range(1, 37)]

    query = """
    INSERT IGNORE INTO estudiante_curso(
        curso_id,
        estudiante_id
    )
    VALUES (%s, %s)
    """

    for inscripcion in inscripciones:
        execute_query(query, inscripcion, modifica_db=True)


def seed_evaluaciones():
    evaluaciones = [
        (
            1,
            1,
            "Primer Parcial",
            "Parcial de estructuras",
            "2026-05-10",
        ),
        (
            1,
            2,
            "TP Integrador",
            "Trabajo práctico grupal",
            "2026-06-15",
        ),
    ]

    query = """
    INSERT IGNORE INTO evaluaciones(
        curso_id,
        tipo_evaluacion_id,
        titulo,
        descripcion,
        fecha
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    for evaluacion in evaluaciones:
        execute_query(query, evaluacion, modifica_db=True)


def seed_notas():
    # alumno_id apunta a estudiantes(id): 1 = Ana (usuario 3), 2 = Lucas (usuario 4)
    notas = [
        (1, 1, None, 8),
        (1, 2, None, 6),
        (2, None, 1, 9),
    ]

    query = """
    INSERT IGNORE INTO notas(
        evaluacion_id,
        alumno_id,
        equipo_id,
        nota
    )
    VALUES (%s, %s, %s, %s)
    """

    for nota in notas:
        execute_query(query, nota, modifica_db=True)


def seed_equipos():
    equipos = [
        (1, 2, "Grupo 1"),
    ]

    query = """
    INSERT IGNORE INTO equipos(
        curso_id,
        evaluacion_id,
        nombre
    )
    VALUES (%s, %s, %s)
    """

    for equipo in equipos:
        execute_query(query, equipo, modifica_db=True)


def seed_equipo_integrantes():
    # alumno_id apunta a estudiantes(id), no a usuarios(id)
    integrantes = [
        (1, 1),
        (1, 2),
    ]

    query = """
    INSERT IGNORE INTO equipo_integrantes(
        equipo_id,
        alumno_id
    )
    VALUES (%s, %s)
    """

    for integrante in integrantes:
        execute_query(query, integrante, modifica_db=True)


def seed_clases():
    # profesor_id=1 apunta a profesores(id), no a usuarios(id). 1 = Juan (usuario_id=2).
    # temas múltiples se separan con " | " — el service los parte en bullets al armar el cronograma.
    # status: finalizada si la fecha ya pasó (hoy ~ 2026-06-03), pendiente si es futura.
    # feriados: tipo=practica, tema=None, tags=["Feriado"], modalidad=None.

    # borra las clases del curso 1 para que el seed sea idempotente
    execute_query("DELETE FROM clases WHERE curso_id = 1", (), modifica_db=True)

    clases = [
        # ── Semana 1 ──────────────────────────────────────────────────────────────
        ("Semana 1 - Teórica", 1, 1, "2026-03-10 10:00:00", "2026-03-10 12:00:00",
         "Presentación de la materia | Introducción a Linux: historia y usos"
         " | FileSystem y carpetas principales"
         " | Terminal y comandos básicos: cd, ls, cat, pwd, cp, mv, rm, mkdir, sudo",
         "finalizada", "teorica", "Virtual", json.dumps([])),
        ("Semana 1 - Práctica", 1, 1, "2026-03-12 14:00:00", "2026-03-12 16:00:00",
         "Opciones de instalación: WSL, VM, Dual Boot | ¿Qué es Bash?"
         " | Editores de terminal | Variables de entorno | Mi primer Script",
         "finalizada", "practica", "Virtual", json.dumps([])),

        # ── Semana 2 ──────────────────────────────────────────────────────────────
        ("Semana 2 - Teórica", 1, 1, "2026-03-17 10:00:00", "2026-03-17 12:00:00",
         "Bash: continuación | Estructuras condicionales e iterativas"
         " | Pipelines y redirecciones | Scripts: búsqueda, reemplazo, manejo de archivos",
         "finalizada", "teorica", "Virtual", json.dumps([])),
        ("Semana 2 - Práctica", 1, 1, "2026-03-19 14:00:00", "2026-03-19 16:00:00",
         "Ejercitación integral de comandos | Consultas Linux | Ejercicios de Scripting",
         "finalizada", "practica", "Presencial", json.dumps(["Obligatoria"])),

        # ── Semana 3 ──────────────────────────────────────────────────────────────
        ("Semana 3 - Teórica", 1, 1, "2026-03-24 10:00:00", "2026-03-24 12:00:00",
         "Introducción a Front End | Intro a Flask | Intro a HTML"
         " | Intro a CSS | Intro a JavaScript | Mi primer código en Flask",
         "finalizada", "teorica", "Virtual", json.dumps([])),
        ("Semana 3 - Práctica", 1, 1, "2026-03-26 14:00:00", "2026-03-26 16:00:00",
         "Flask con HTML + CSS (ejemplo asistido)",
         "finalizada", "practica", "Virtual", json.dumps([])),

        # ── Semana 4 ──────────────────────────────────────────────────────────────
        ("Semana 4 - Teórica", 1, 1, "2026-03-31 10:00:00", "2026-03-31 12:00:00",
         "HTML: estructura básica | Etiquetas: div, p, a, img, ul/ol, table, form, input, button"
         " | CSS: clases e IDs | Atributos de estilo: color, display, font, margin, padding, border"
         " | Flexbox",
         "finalizada", "teorica", "Virtual", json.dumps([])),
        ("Semana 4 - Práctica", 1, 1, "2026-04-02 14:00:00", "2026-04-02 16:00:00",
         "JavaScript + HTML | Ejercitación",
         "finalizada", "practica", "Virtual", json.dumps([])),

        # ── Semana 5 ──────────────────────────────────────────────────────────────
        ("Semana 5 - Teórica", 1, 1, "2026-04-07 10:00:00", "2026-04-07 12:00:00",
         "JavaScript",
         "finalizada", "teorica", "Virtual", json.dumps([])),
        ("Semana 5 - Práctica", 1, 1, "2026-04-09 14:00:00", "2026-04-09 16:00:00",
         "Ejercitación integral Flask + JavaScript + HTML",
         "finalizada", "practica", "Presencial", json.dumps(["Obligatoria"])),

        # ── Semana 6 ──────────────────────────────────────────────────────────────
        ("Semana 6 - Teórica", 1, 1, "2026-04-14 10:00:00", "2026-04-14 12:00:00",
         "API RESTful (Python): qué es una API, qué es REST | Ejemplo de API",
         "finalizada", "teorica", "Virtual", json.dumps(["Parcialito"])),
        ("Semana 6 - Feriado", 1, 1, "2026-04-16 14:00:00", "2026-04-16 16:00:00",
         None,
         "finalizada", "practica", None, json.dumps(["Feriado"])),

        # ── Semana 7 ──────────────────────────────────────────────────────────────
        ("Semana 7 - Teórica", 1, 1, "2026-04-21 10:00:00", "2026-04-21 12:00:00",
         "Testing",
         "finalizada", "teorica", "Virtual", json.dumps([])),
        ("Semana 7 - Práctica", 1, 1, "2026-04-23 14:00:00", "2026-04-23 16:00:00",
         "Depuración (debugging) | Ejercitación de debugging",
         "finalizada", "practica", "Virtual", json.dumps([])),

        # ── Semana 8 ──────────────────────────────────────────────────────────────
        ("Semana 8 - Teórica", 1, 1, "2026-04-28 10:00:00", "2026-04-28 12:00:00",
         "Introducción a la agilidad | Kanban"
         " | Herramientas: Jira, Trello, Asana, Basecamp | CI/CD",
         "finalizada", "teorica", "Virtual", json.dumps([])),
        ("Semana 8 - Feriado", 1, 1, "2026-04-30 14:00:00", "2026-04-30 16:00:00",
         None,
         "finalizada", "practica", None, json.dumps(["Feriado"])),

        # ── Semana 9 ──────────────────────────────────────────────────────────────
        ("Semana 9 - Teórica", 1, 1, "2026-05-05 10:00:00", "2026-05-05 12:00:00",
         "Consultas previas al 1er parcial",
         "finalizada", "teorica", "Virtual", json.dumps([])),
        ("Semana 9 - 1er Parcial", 1, 1, "2026-05-07 14:00:00", "2026-05-07 16:00:00",
         "1er Parcial: todo lo visto hasta el momento, incluye Backend",
         "finalizada", "practica", "Presencial", json.dumps(["1er Parcial", "Obligatoria"])),

        # ── Semana 10 ─────────────────────────────────────────────────────────────
        ("Semana 10 - Teórica", 1, 1, "2026-05-12 10:00:00", "2026-05-12 12:00:00",
         "SQL: qué es una BDD, qué es SQL | Estructura de BDD relacionales"
         " | CREATE / DROP TABLE | SELECT - FROM - WHERE",
         "finalizada", "teorica", "Virtual", json.dumps(["Armado de grupos TP"])),
        ("Semana 10 - Práctica", 1, 1, "2026-05-14 14:00:00", "2026-05-14 16:00:00",
         "SQL: tipos de datos | INSERT, UPDATE, DELETE | AUTO_INCREMENT, Primary Key",
         "finalizada", "practica", "Virtual", json.dumps([])),

        # ── Semana 11 ─────────────────────────────────────────────────────────────
        ("Semana 11 - Teórica", 1, 1, "2026-05-19 10:00:00", "2026-05-19 12:00:00",
         "Ejercitación integral Front + Backend"
         " | Crear API consumiendo datos de una base | SQL Joins",
         "finalizada", "teorica", "Presencial", json.dumps(["Obligatoria"])),
        ("Semana 11 - Práctica", 1, 1, "2026-05-21 14:00:00", "2026-05-21 16:00:00",
         "Git: qué es y para qué sirve | Repositorio y estados"
         " | Comandos: status, add, commit, push, pull, clone"
         " | GitHub: diferencia con Git, SSH",
         "finalizada", "practica", "Virtual", json.dumps(["Entrega parcial TP"])),

        # ── Semana 12 ─────────────────────────────────────────────────────────────
        ("Semana 12 - Teórica", 1, 1, "2026-05-26 10:00:00", "2026-05-26 12:00:00",
         "Git: ramas (checkout, branch) | git restore, staging | git log y git diff",
         "finalizada", "teorica", "Virtual", json.dumps(["Entrega parcial TP"])),
        ("Semana 12 - Práctica", 1, 1, "2026-05-28 14:00:00", "2026-05-28 16:00:00",
         "Docker: qué es, para qué se usa | Diferencia con VM | Containers e imágenes"
         " | Comandos: run, ps, exec, start, stop, rm, images, pull",
         "finalizada", "practica", "Virtual", json.dumps([])),

        # ── Semana 13 ─────────────────────────────────────────────────────────────
        ("Semana 13 - Teórica", 1, 1, "2026-06-02 10:00:00", "2026-06-02 12:00:00",
         "Consultas TP | Presentación de ramas a utilizar | Vistas HTML, avances en API",
         "finalizada", "teorica", "Virtual", json.dumps(["Entrega parcial TP"])),
        ("Semana 13 - Práctica", 1, 1, "2026-06-04 14:00:00", "2026-06-04 16:00:00",
         "Docker: Dockerfile | Volúmenes y puertos | docker build"
         " | Docker Compose: compose.yaml, build, up, stop, down",
         "pendiente", "practica", "Virtual", json.dumps([])),

        # ── Semana 14 ─────────────────────────────────────────────────────────────
        ("Semana 14 - Teórica", 1, 1, "2026-06-09 10:00:00", "2026-06-09 12:00:00",
         "Consultas | Integración Front y Back",
         "pendiente", "teorica", "Virtual", json.dumps(["Entrega documentación de endpoints"])),
        ("Semana 14 - 1er Recuperatorio", 1, 1, "2026-06-11 14:00:00", "2026-06-11 16:00:00",
         "1er Recuperatorio",
         "pendiente", "practica", "Presencial", json.dumps(["1er Recuperatorio", "Obligatoria"])),

        # ── Semana 15 ─────────────────────────────────────────────────────────────
        ("Semana 15 - Teórica", 1, 1, "2026-06-16 10:00:00", "2026-06-16 12:00:00",
         "Consultas finales TP",
         "pendiente", "teorica", "Virtual", json.dumps(["Entrega +80% TP"])),
        ("Semana 15 - Entrega TP", 1, 1, "2026-06-18 14:00:00", "2026-06-18 16:00:00",
         "1er Entrega TP Integrador y Defensa",
         "pendiente", "practica", "Presencial", json.dumps(["Entrega TP", "Obligatoria"])),

        # ── Semana 16 ─────────────────────────────────────────────────────────────
        ("Semana 16 - Teórica", 1, 1, "2026-06-23 10:00:00", "2026-06-23 12:00:00",
         "Defensas presenciales | Consultas TP",
         "pendiente", "teorica", "Presencial", json.dumps(["Obligatoria"])),
        ("Semana 16 - 2da Entrega TP", 1, 1, "2026-06-25 14:00:00", "2026-06-25 16:00:00",
         "2da Entrega TP Integrador y Defensa",
         "pendiente", "practica", "Presencial", json.dumps(["Entrega TP", "Obligatoria"])),

        # ── Semana 17 ─────────────────────────────────────────────────────────────
        ("Semana 17 - Teórica", 1, 1, "2026-06-30 10:00:00", "2026-06-30 12:00:00",
         "Cierre de la materia | Defensas presenciales",
         "pendiente", "teorica", "Presencial", json.dumps(["Obligatoria"])),
        ("Semana 17 - Final", 1, 1, "2026-07-02 14:00:00", "2026-07-02 16:00:00",
         "2do Recuperatorio | 1er Fecha Final",
         "pendiente", "practica", "Presencial", json.dumps(["2do Recuperatorio", "Final", "Obligatoria"])),
    ]

    query = """
    INSERT INTO clases (
        nombre,
        profesor_id,
        curso_id,
        fecha_hora_inicio,
        fecha_hora_fin,
        tema,
        status,
        tipo,
        modalidad,
        tags
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for clase in clases:
        execute_query(query, clase, modifica_db=True)


def seed_qr_asistencia():
    qr = [
        (
            1,
            "token-demo-123",
            "2026-12-31 23:59:59",
        ),
    ]

    query = """
    INSERT IGNORE INTO qr_asistencia(
        clase_id,
        token,
        expiracion
    )
    VALUES (%s, %s, %s)
    """

    for item in qr:
        execute_query(query, item, modifica_db=True)


def seed_asistencias():
    # alumno_id apunta a estudiantes(id), no a usuarios(id)
    asistencias = [
        (1, 1),
        (1, 2),
    ]

    query = """
    INSERT IGNORE INTO asistencias(
        clase_id,
        alumno_id
    )
    VALUES (%s, %s)
    """

    for asistencia in asistencias:
        execute_query(query, asistencia, modifica_db=True)


def seed_materiales():
    materiales = [
        (
            1,
            "Clase 1 PDF",
            "https://storage.com/clase1.pdf",
            2,
        ),
    ]

    query = """
    INSERT IGNORE INTO materiales(
        curso_id,
        titulo,
        archivo_url,
        subido_por
    )
    VALUES (%s, %s, %s, %s)
    """

    for material in materiales:
        execute_query(query, material, modifica_db=True)


def seed_logs():
    logs = [
        (
            1,
            "LOGIN",
            "/auth/login",
            "POST",
            "Inicio de sesión correcto",
        ),
    ]

    query = """
    INSERT IGNORE INTO logs(
        usuario_id,
        accion,
        endpoint,
        metodo,
        detalle
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    for log in logs:
        execute_query(query, log, modifica_db=True)


def run_seed():
    print("Seeding database...")

    seed_materias()
    seed_tipos_evaluacion()
    seed_usuarios()
    seed_estudiantes()
    seed_profesores()
    seed_cursos()
    seed_curso_docentes()
    seed_inscripciones()
    seed_evaluaciones()
    seed_equipos()
    seed_equipo_integrantes()
    seed_notas()
    seed_clases()
    seed_qr_asistencia()
    seed_asistencias()
    seed_materiales()
    seed_logs()

    print("Seed completado correctamente.")


if __name__ == "__main__":
    run_seed()