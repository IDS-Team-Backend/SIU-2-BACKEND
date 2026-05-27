import db

TABLAS = [
    "logs",
    "materiales",
    "asistencias",
    "qr_asistencia",
    "clases",
    "equipo_integrantes",
    "notas",
    "equipos",
    "evaluaciones",
    "curso_usuarios",
    "cursos",
    "profesores",
    "estudiantes",
    "usuarios",
    "tipos_evaluacion",
    "materias",
]


def limpiar_datos():
    conn = None
    cursor = None
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for tabla in TABLAS:
            print(f"Truncando {tabla}...")
            cursor.execute(f"TRUNCATE TABLE {tabla};")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        conn.commit()
        print("¡Datos eliminados! Las tablas quedaron vacías y los AUTO_INCREMENT reseteados.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error al limpiar la base de datos: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    limpiar_datos()
