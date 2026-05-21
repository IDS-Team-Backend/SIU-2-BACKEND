from db import execute_query
from werkzeug.security import generate_password_hash

def seed_tipos_usuario():
    tipos = [
        ("admin",),
        ("docente",),
        ("alumno",),
        ("ayudante",)
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
        ("Admin", "Sistema", "admin@fiuba.edu.ar", 1000, password, 1),
        ("Juan", "Perez", "juan@fiuba.edu.ar", 1001, password, 2),
        ("Ana", "Gomez", "ana@fiuba.edu.ar", 1002, password, 3),
        ("Lucas", "Martinez", "lucas@fiuba.edu.ar", 1003, password, 3),
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
        (1, 3, 8),
        (1, 4, 6)
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
        ("Clase 1", 2, 1, "2026-05-15 09:00:00", "Introducción a la materia", "finalizada"),
        ("Clase 2", 2, 1, "2026-05-20 14:30:00", "Listas enlazadas y estructuras", "finalizada"),
        ("Clase 3", 2, 2, "2026-05-22 18:00:00", "Consultas avanzadas en SQL", "en curso"),
        ("Clase 4", 2, 2, "2026-05-25 10:00:00", "Arquitectura en 3 Capas", "pendiente"),
        ("Clase 5", 2, 1, "2026-06-01 16:00:00", "Optimización de Bases de Datos", "pendiente")
    ]

    query = """
    INSERT IGNORE INTO clases (
        nombre,
        profesor_id,
        curso_id,
        fecha_hora,
        tema,
        status
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    for clase in clases:
        execute_query(query, clase, modifica_db=True)

def seed_asistencias():
    asistencias = [
        (1, 3),
        (1, 4)
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
    seed_cursos()
    seed_inscripciones()
    seed_evaluaciones()
    seed_notas()
    seed_clases()
    seed_asistencias()

    print("Seed completado correctamente.")

if __name__ == "__main__":
    run_seed()