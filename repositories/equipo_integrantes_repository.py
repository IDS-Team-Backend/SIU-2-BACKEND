import db

def obtener_integrantes(equipo_id=None,alumno_id=None):
    query = """
        FROM equipo_integrantes ei
        INNER JOIN estudiantes e
            ON e.id = ei.alumno_id
        INNER JOIN usuarios u
            ON u.id = e.usuario_id
        WHERE 1=1
    """
    params = []
    if equipo_id:
        query += " AND ei.equipo_id = %s"
        params.append(equipo_id)
    if alumno_id:
        query += " AND ei.alumno_id = %s"
        params.append(alumno_id)
    count_query = """
        SELECT COUNT(*) as total
    """ + query
    count_integrantes = db.execute_query(
        count_query,
        tuple(params),
        un_solo_valor=True
    )
    total = (
        count_integrantes["total"]
        if count_integrantes
        else 0
    )
    select_query = """
        SELECT
            ei.equipo_id,
            ei.alumno_id,
            u.nombre,
            u.apellido,
            u.email,
            u.activo
    """ + query
    integrantes = db.execute_query(
        select_query,
        tuple(params)
    )

    return integrantes, total

def agregar_integrante(equipo_id,alumno_id):
    query = """
        INSERT INTO equipo_integrantes
        (
            equipo_id,
            alumno_id
        )
        VALUES (%s, %s)
    """
    params = (
        equipo_id,
        alumno_id
    )
    db.execute_query(
        query,
        params,
        modifica_db=True
    )
    return {
        "equipo_id": equipo_id,
        "alumno_id": alumno_id
    }

def eliminar_integrante(equipo_id,alumno_id):
    query = """
        DELETE FROM equipo_integrantes
        WHERE equipo_id = %s
        AND alumno_id = %s
    """
    filas = db.execute_query(
        query,
        (equipo_id, alumno_id),
        modifica_db=True
    )
    return filas > 0

def existe_integrante(equipo_id,alumno_id):
    query = """
        SELECT COUNT(*) as total
        FROM equipo_integrantes
        WHERE equipo_id = %s
        AND alumno_id = %s
    """
    result = db.execute_query(
        query,
        (equipo_id, alumno_id),
        un_solo_valor=True
    )
    return result["total"] > 0 if result else False