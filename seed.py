from db import execute_query
from werkzeug.security import generate_password_hash


def seed_tipos_usuario():
    tipos = [
        (1, "admin"),
        (2, "profesor"),
        (3, "alumno"),
        (4, "ayudante"),
    ]

    query = """
    INSERT IGNORE INTO tipos_usuario(id, nombre)
    VALUES (%s, %s)
    """

    for tipo in tipos:
        execute_query(query, tipo, modifica_db=True)


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
    password = generate_password_hash("1234")

    usuarios = [
        (
            "Admin",
            "Sistema",
            "admin@fiuba.edu.ar",
            1000,
            password,
            1,
        ),
        (
            "Juan",
            "Perez",
            "juan@fiuba.edu.ar",
            1001,
            password,
            2,
        ),
        (
            "Ana",
            "Gomez",
            "ana@fiuba.edu.ar",
            1002,
            password,
            3,
        ),
        (
            "Lucas",
            "Martinez",
            "lucas@fiuba.edu.ar",
            1003,
            password,
            3,
        ),
        (
            "Pedro",
            "Ruiz",
            "pedro@fiuba.edu.ar",
            1004,
            password,
            4,
        ),
    ]

    query = """
    INSERT IGNORE INTO usuarios(
        nombre,
        apellido,
        email,
        dni,
        password_hash,
        rol_id
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    for usuario in usuarios:
        execute_query(query, usuario, modifica_db=True)


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


def seed_inscripciones():
    inscripciones = [
        (1, 3),
        (1, 4),
        (1, 5),
    ]

    query = """
    INSERT IGNORE INTO curso_usuarios(
        curso_id,
        usuario_id
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
    notas = [
        (1, 3, None, 8),
        (1, 4, None, 6),
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
    integrantes = [
        (1, 3),
        (1, 4),
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
    clases = [
        (1, "2026-05-15", "Introducción"),
        (1, "2026-05-20", "Listas enlazadas"),
    ]

    query = """
    INSERT IGNORE INTO clases(
        curso_id,
        fecha,
        tema
    )
    VALUES (%s, %s, %s)
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
    asistencias = [
        (1, 3),
        (1, 4),
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

    seed_tipos_usuario()
    seed_materias()
    seed_tipos_evaluacion()
    seed_usuarios()
    seed_cursos()
    seed_inscripciones()
    seed_evaluaciones()
    seed_notas()
    seed_equipos()
    seed_equipo_integrantes()
    seed_clases()
    seed_qr_asistencia()
    seed_asistencias()
    seed_materiales()
    seed_logs()

    print("Seed completado correctamente.")


if __name__ == "__main__":
    run_seed()