import db


def docente_pertenece_activamente_a_curso(docente_id, curso_id):
    query = """
        SELECT 1
        FROM curso_docentes
        WHERE docente_id = %s
          AND curso_id = %s
        LIMIT 1
    """
    resultado = db.execute_query(query, (docente_id, curso_id), un_solo_valor=True)
    return resultado is not None


def obtener_por_curso(curso_id):
    query = """
        SELECT
            cd.id,
            cd.curso_id,
            cd.docente_id,
            cd.nombre AS rol,
            p.legajo,
            u.nombre,
            u.apellido,
            u.email
        FROM curso_docentes cd
        INNER JOIN profesores p ON cd.docente_id = p.id
        INNER JOIN usuarios u ON p.usuario_id = u.id
        WHERE cd.curso_id = %s
        ORDER BY cd.id ASC
    """
    return db.execute_query(query, (curso_id,)) or []


def obtener_por_docentes(docente_ids):
    """Participaciones (curso + rol) de varios docentes en una sola query.
    Devuelve una fila por (docente, curso) para agrupar luego por docente_id."""
    if not docente_ids:
        return []
    placeholders = ", ".join(["%s"] * len(docente_ids))
    query = f"""
        SELECT
            cd.docente_id,
            cd.nombre AS rol,
            c.id AS curso_id,
            c.nombre AS curso_nombre,
            c.anio,
            c.cuatrimestre,
            c.activa
        FROM curso_docentes cd
        INNER JOIN cursos c ON cd.curso_id = c.id
        WHERE cd.docente_id IN ({placeholders})
        ORDER BY c.anio DESC, c.cuatrimestre DESC, c.id ASC
    """
    return db.execute_query(query, tuple(docente_ids)) or []


def obtener_por_id(id):
    query = """
        SELECT
            cd.id,
            cd.curso_id,
            cd.docente_id,
            cd.nombre AS rol,
            p.legajo,
            u.nombre,
            u.apellido,
            u.email
        FROM curso_docentes cd
        INNER JOIN profesores p ON cd.docente_id = p.id
        INNER JOIN usuarios u ON p.usuario_id = u.id
        WHERE cd.id = %s
    """
    return db.execute_query(query, (id,), un_solo_valor=True)


def existe(curso_id, docente_id):
    query = """
        SELECT COUNT(*) AS total
        FROM curso_docentes
        WHERE curso_id = %s AND docente_id = %s
    """
    resultado = db.execute_query(query, (curso_id, docente_id), un_solo_valor=True)
    return resultado["total"] > 0 if resultado else False


def agregar(curso_id, docente_id, rol):
    query = """
        INSERT INTO curso_docentes (curso_id, docente_id, nombre)
        VALUES (%s, %s, %s)
    """
    nuevo_id = db.execute_query(query, (curso_id, docente_id, rol), modifica_db=True)
    return obtener_por_id(nuevo_id)


def cambiar_rol(id, rol):
    query = "UPDATE curso_docentes SET nombre = %s WHERE id = %s"
    filas = db.execute_query(query, (rol, id), modifica_db=True)
    return filas > 0


def eliminar(id):
    query = "DELETE FROM curso_docentes WHERE id = %s"
    filas = db.execute_query(query, (id,), modifica_db=True)
    return filas > 0