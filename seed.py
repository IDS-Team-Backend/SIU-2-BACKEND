from db import execute_query
from werkzeug.security import generate_password_hash

def seed_tipos_usuario():
    tipos = [
        ("admin",),
        ("docente",),
        ("alumno",)
    ]

    query = """
    INSERT IGNORE INTO tipos_usuario(nombre)
    VALUES (%s)
    """

    for tipo in tipos:
        execute_query(query, tipo, modifica_db=True)

def seed_materias():
    materias = [
        ("Algoritmos y Programación", "75.40"),
        ("Base de Datos", "75.06"),
        ("Organización de Datos", "75.41")
    ]

    query = """
    INSERT IGNORE INTO materias(nombre, codigo)
    VALUES (%s, %s)
    """

    for materia in materias:
        execute_query(query, materia, modifica_db=True)

def seed_tipos_evaluacion():
    tipos = [
        ("Parcial",),
        ("TP",),
        ("Final",)
    ]

    query = """
    INSERT IGNORE INTO tipos_evaluacion(nombre)
    VALUES (%s)
    """

    for tipo in tipos:
        execute_query(query, tipo, modifica_db=True)

def seed_usuarios():
    password = generate_password_hash("1234")

    usuarios = [
        ("Admin", "Sistema", "admin@fiuba.edu.ar", 30000000, password, 1),
        ("Juan", "Perez", "juan@fiuba.edu.ar", 30000001, password, 2),
        ("Ana", "Gomez", "ana@fiuba.edu.ar", 30000002, password, 3),
        ("Lucas", "Martinez", "lucas@fiuba.edu.ar", 30000003, password, 3),
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

def seed_estudiantes():
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

def seed_cursos():
    cursos = [
        (1, "Curso A", 2026, 1),
        (2, "Curso B", 2026, 1)
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
        (1, 4)
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
            "2026-05-10"
        )
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
        (1, 1, 8),
        (1, 2, 6)
    ]

    query = """
    INSERT IGNORE INTO notas(
        evaluacion_id,
        alumno_id,
        nota
    )
    VALUES (%s, %s, %s)
    """

    for nota in notas:
        execute_query(query, nota, modifica_db=True)

def seed_clases():
    clases = [
        (1, "2026-05-15", "Introducción"),
        (1, "2026-05-20", "Listas enlazadas")
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

def seed_asistencias():
    asistencias = [
        (1, 1),
        (1, 2)
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

def run_seed():
    print("Seeding database...")

    seed_tipos_usuario()
    seed_materias()
    seed_tipos_evaluacion()
    seed_usuarios()
    seed_estudiantes()
    seed_cursos()
    seed_inscripciones()
    seed_evaluaciones()
    seed_notas()
    seed_clases()
    seed_asistencias()

    print("Seed completado correctamente.")

if __name__ == "__main__":
    run_seed()