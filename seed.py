import json
import random
from datetime import datetime, timedelta
from uuid import uuid4
from db import execute_query
from werkzeug.security import generate_password_hash


def seed_materias():
    materias = [
        ("Introducción al Desarrollo de Software", "75.40"),
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
        ("Tomas",      "Vargas",      "tvargas@fi.uba.ar",      44100005, password, False),
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
    ADMIN_ID = 1
    PROFESORES_IDS = {2, 5, 6}
    estudiante_uids = [uid for uid in range(1, 38) if uid != ADMIN_ID and uid not in PROFESORES_IDS]
    estudiantes = [
        (uid, 100000 + uid - 1, C[i % len(C)], 2024, str(uuid4()))
        for i, uid in enumerate(estudiante_uids)
    ]

    query = """
    INSERT IGNORE INTO estudiantes(
        usuario_id,
        padron,
        carrera,
        anio_ingreso,
        token_qr
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    for estudiante in estudiantes:
        execute_query(query, estudiante, modifica_db=True)


def seed_profesores():
    profesores = [
        (2, 500001, "Ingeniero en Informática", "Informática", "2018-03-01"),
        (5, 500002, "Licenciado en Sistemas", "Informática", "2020-04-15"),
        (6, 500003, "Analista de Sistemas", "Informática", "2022-08-10"),
        (7, 500004, "Ingeniero en Informática", "Informática", "2021-07-02"),
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
    # Una sola cátedra (materia 1) que avanza cuatri a cuatri: la cursada actual
    # es la activa; la del cuatrimestre anterior queda finalizada (cursada anterior).
    DESC = ("Materia introductoria al desarrollo de software con Python. Cubre Git, "
            "desarrollo web con Flask, APIs REST, bases de datos SQL, testing y Docker.")
    cursos = [
        (1, "2026 · 1º cuatrimestre", 2026, 1, DESC,
         "Virtual con presenciales obligatorias", "Ingeniería en Informática", 6, "abierta", True),
        (1, "2025 · 2º cuatrimestre", 2025, 2, DESC,
         "Virtual con presenciales obligatorias", "Ingeniería en Informática", 6, "finalizada", False),
    ]

    query = """
    INSERT IGNORE INTO cursos(
        materia_id,
        nombre,
        anio,
        cuatrimestre,
        descripcion,
        modalidad,
        carrera,
        horas_semanales,
        estado,
        activa
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for curso in cursos:
        execute_query(query, curso, modifica_db=True)

def seed_curso_docentes():
    curso_docentes = [
        (1, 1, "titular"),
        (2, 1, "titular"),
        (1, 2, "jefe_tp"),
        (1, 3, "ayudante"),
        (1, 4, "colaborador")
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
    estudiante_ids = [r["id"] for r in execute_query("SELECT id FROM estudiantes ORDER BY id")]
    inscripciones = [(1, eid) for eid in estudiante_ids]

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
        (1, 1, "Primer Parcial",   "Parcial de estructuras",    "2026-05-10"),
        (1, 2, "TP Integrador",    "Trabajo práctico grupal",   "2026-06-15"),
        (1, 1, "Segundo Parcial",  "Parcial de bases de datos", "2026-06-20"),
        (1, 3, "Final",            "Examen final integrador",   "2026-07-02"),
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


def seed_equipos():
    # 6 grupos de ~5 alumnos para el TP Integrador (evaluacion_id=2)
    equipos = [
        (1, 2, "Grupo 1"),
        (1, 2, "Grupo 2"),
        (1, 2, "Grupo 3"),
        (1, 2, "Grupo 4"),
        (1, 2, "Grupo 5"),
        (1, 2, "Grupo 6"),
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
    # Obtenemos todos los estudiante_ids inscritos en curso 1
    estudiante_ids = [r["id"] for r in execute_query("SELECT id FROM estudiantes ORDER BY id")]

    # Distribuimos los estudiantes en 6 grupos de ~5
    integrantes = []
    for idx, eid in enumerate(estudiante_ids):
        equipo_id = (idx % 6) + 1
        integrantes.append((equipo_id, eid))

    query = """
    INSERT IGNORE INTO equipo_integrantes(
        equipo_id,
        alumno_id
    )
    VALUES (%s, %s)
    """

    for integrante in integrantes:
        execute_query(query, integrante, modifica_db=True)


def seed_notas():
    """
    Genera notas realistas para los 34 estudiantes:
    - Evaluacion 1 (Parcial):      notas individuales, distribución normal centrada en 6.5
    - Evaluacion 2 (TP grupal):    notas por equipo, más altas (7-10)
    - Evaluacion 3 (2do Parcial):  notas individuales, distribución normal centrada en 7
    - Evaluacion 4 (Final):        solo aprox. la mitad rinde, notas más variadas

    Además, ~4 estudiantes "abandonan" (no tienen notas en las últimas evaluaciones).
    """
    random.seed(42)  # reproducible

    estudiante_ids = [r["id"] for r in execute_query("SELECT id FROM estudiantes ORDER BY id")]
    total = len(estudiante_ids)

    # Los últimos 4 se marcan como "abandono" — solo tienen nota del primer parcial
    abandonan = set(estudiante_ids[-4:])
    activos = [eid for eid in estudiante_ids if eid not in abandonan]

    query = """
    INSERT IGNORE INTO notas(
        evaluacion_id,
        alumno_id,
        equipo_id,
        nota
    )
    VALUES (%s, %s, %s, %s)
    """

    def nota_clamp(valor):
        return max(1, min(10, round(valor)))

    # ── Evaluacion 1: Primer Parcial (individual) ──────────────────────────────
    # Distribución: mayoría entre 5-8, algunos aplazados (1-3), pocos sobresalientes (9-10)
    perfiles_parcial1 = {
        "excelente":  (list(estudiante_ids[:5]),  lambda: nota_clamp(random.gauss(9.2, 0.5))),
        "bueno":      (list(estudiante_ids[5:18]), lambda: nota_clamp(random.gauss(7.0, 0.8))),
        "regular":    (list(estudiante_ids[18:28]),lambda: nota_clamp(random.gauss(5.5, 0.9))),
        "bajo":       (list(estudiante_ids[28:]),  lambda: nota_clamp(random.gauss(3.5, 1.0))),
    }
    for _, (eids, gen_nota) in perfiles_parcial1.items():
        for eid in eids:
            execute_query(query, (1, eid, None, gen_nota()), modifica_db=True)

    # ── Evaluacion 2: TP Integrador (grupal) ──────────────────────────────────
    # Nota por equipo: grupos buenos 8-10, grupos regulares 6-7
    notas_por_equipo = {
        1: nota_clamp(random.gauss(9.0, 0.4)),
        2: nota_clamp(random.gauss(8.5, 0.4)),
        3: nota_clamp(random.gauss(7.5, 0.5)),
        4: nota_clamp(random.gauss(7.0, 0.5)),
        5: nota_clamp(random.gauss(8.0, 0.4)),
        6: nota_clamp(random.gauss(6.5, 0.6)),
    }
    integrantes_rows = execute_query(
        "SELECT equipo_id, alumno_id FROM equipo_integrantes ORDER BY equipo_id"
    )
    for row in integrantes_rows:
        eid = row["alumno_id"]
        if eid in abandonan:
            continue
        equipo_id = row["equipo_id"]
        # Equipos 5 y 6 quedan sin nota para mostrar los estados de entrega
        # "Entregado (sin corregir)" y "No entregado" en la record page.
        if equipo_id in (5, 6):
            continue
        nota = notas_por_equipo[equipo_id]
        execute_query(query, (2, None, equipo_id, nota), modifica_db=True)

    # ── Evaluacion 3: Segundo Parcial (individual, solo activos) ──────────────
    # Mejora leve respecto al primero (aprendieron)
    for eid in activos:
        # Heredamos el "perfil" aproximado del alumno según su posición
        idx = estudiante_ids.index(eid)
        if idx < 5:
            nota = nota_clamp(random.gauss(9.3, 0.5))
        elif idx < 18:
            nota = nota_clamp(random.gauss(7.5, 0.7))
        elif idx < 28:
            nota = nota_clamp(random.gauss(6.2, 0.9))
        else:
            nota = nota_clamp(random.gauss(4.5, 1.0))
        execute_query(query, (3, eid, None, nota), modifica_db=True)

    # ── Evaluacion 4: Final (solo los que aprobaron ambos parciales) ──────────
    # Rinden ~60% de los activos
    rinden_final = random.sample(activos, k=int(len(activos) * 0.60))
    for eid in rinden_final:
        idx = estudiante_ids.index(eid)
        if idx < 5:
            nota = nota_clamp(random.gauss(9.0, 0.6))
        elif idx < 18:
            nota = nota_clamp(random.gauss(7.0, 1.0))
        else:
            nota = nota_clamp(random.gauss(6.0, 1.2))
        execute_query(query, (4, eid, None, nota), modifica_db=True)


def seed_entregas():
    """
    Entregas del TP Integrador (evaluacion_id=2, grupal), una por equipo.
    Combinadas con las notas, ejercitan los estados de la record page:
      - equipos 1-4: entrega + nota   -> Corregido (con badge entregado/tarde/rehacer)
      - equipo 5:    entrega sin nota  -> Entregado (sin corregir)
      - equipo 6:    sin entrega       -> No entregado
    """
    entregas = [
        # evaluacion_id, equipo_id, fecha_entrega, estado, archivo_url
        (2, 1, "2026-06-18 14:05:00", "entregado", "https://drive.example.com/tp/grupo1.pdf"),
        (2, 2, "2026-06-18 13:50:00", "entregado", "https://drive.example.com/tp/grupo2.pdf"),
        (2, 3, "2026-06-19 09:20:00", "tarde",     "https://drive.example.com/tp/grupo3.pdf"),
        (2, 4, "2026-06-18 14:00:00", "rehacer",   "https://drive.example.com/tp/grupo4.pdf"),
        (2, 5, "2026-06-18 14:10:00", "entregado", "https://drive.example.com/tp/grupo5.pdf"),
    ]

    query = """
    INSERT IGNORE INTO entregas(
        evaluacion_id,
        equipo_id,
        fecha_entrega,
        estado,
        archivo_url
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    for entrega in entregas:
        execute_query(query, entrega, modifica_db=True)


def seed_clases():
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


def seed_asistencias():
    """
    Genera asistencias realistas para todas las clases finalizadas del curso 1.

    Perfiles de asistencia por alumno (mismo seed que notas para consistencia):
    - Muy constante (top 5):    85-100% de presencia
    - Regular (siguientes 20):  60-85%
    - Irregular (siguientes 5): 30-60%
    - Abandonadores (últimos 4): solo primeras 4 clases (~30%)
    """
    random.seed(42)

    clases_rows = execute_query(
        "SELECT id FROM clases WHERE curso_id = 1 AND status = 'finalizada' ORDER BY fecha_hora_inicio"
    )
    clase_ids = [r["id"] for r in clases_rows]

    estudiante_ids = [r["id"] for r in execute_query("SELECT id FROM estudiantes ORDER BY id")]

    # Definimos probabilidad de asistir por alumno
    probs = {}
    for idx, eid in enumerate(estudiante_ids):
        if idx < 5:
            probs[eid] = 0.92       # muy constantes
        elif idx < 25:
            probs[eid] = 0.72       # regulares
        elif idx < 30:
            probs[eid] = 0.45       # irregulares
        else:
            probs[eid] = 0.25       # abandonadores (van poco desde el principio)

    # Los "abandonadores" solo pueden asistir a las primeras 4 clases
    abandonadores = set(estudiante_ids[-4:])

    query = """
    INSERT IGNORE INTO asistencias(
        clase_id,
        alumno_id
    )
    VALUES (%s, %s)
    """

    for clase_idx, clase_id in enumerate(clase_ids):
        for eid in estudiante_ids:
            # Abandonadores solo asisten a las primeras 4 clases
            if eid in abandonadores and clase_idx >= 4:
                continue
            if random.random() < probs[eid]:
                execute_query(query, (clase_id, eid), modifica_db=True)


def seed_materiales():
    materiales = [
        (1, "Clase 1 PDF", "https://storage.com/clase1.pdf", 2),
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
        (1, "LOGIN", "/auth/login", "POST", "Inicio de sesión correcto"),
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
    seed_entregas()
    seed_clases()
    seed_asistencias()
    seed_materiales()
    seed_logs()

    print("Seed completado correctamente.")


if __name__ == "__main__":
    run_seed()