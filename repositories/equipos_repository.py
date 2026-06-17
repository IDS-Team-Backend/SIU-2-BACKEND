import db

def obtener_equipos(
    curso_id=None,
    evaluacion_id=None,
    nombre=None
):
    query = """
        FROM equipos e
        WHERE e.deleted_at IS NULL
    """
    params = []
    if curso_id:
        query += " AND e.curso_id = %s"
        params.append(curso_id)
    if evaluacion_id:
        query += " AND e.evaluacion_id = %s"
        params.append(evaluacion_id)
    if nombre:
        query += " AND e.nombre LIKE %s"
        params.append(f"%{nombre}%")

    count_query = """
        SELECT COUNT(*) as total
    """ + query
    count_equipos = db.execute_query(
        count_query,
        tuple(params),
        un_solo_valor=True
    )
    total = (
        count_equipos["total"]
        if count_equipos
        else 0
    )
    select_query = """
        SELECT
            e.id,
            e.curso_id,
            e.evaluacion_id,
            e.nombre,
            e.created_at
    """ + query + " ORDER BY e.id ASC"

    lista_equipos = db.execute_query(
        select_query,
        tuple(params)
    )

    return lista_equipos, total

def crear_equipo(
    curso_id,
    evaluacion_id,
    nombre
):
    query = """
        INSERT INTO equipos
        (
            curso_id,
            evaluacion_id,
            nombre
        )
        VALUES (%s, %s, %s)
    """
    params = (
        curso_id,
        evaluacion_id,
        nombre
    )
    new_id = db.execute_query(
        query,
        params,
        modifica_db=True
    )
    return obtener_equipo_por_id(new_id)

def obtener_equipo_por_id(id):
    query = """
        SELECT
            e.id,
            e.curso_id,
            e.evaluacion_id,
            e.nombre,
            e.created_at
        FROM equipos e
        WHERE e.id = %s
    """
    resultado = db.execute_query(
        query,
        (id,),
        un_solo_valor=True
    )

    return resultado

def obtener_nombres_equipos(evaluacion_id):
    """Nombres de los equipos activos de la evaluación. Una sola query para que la
    carga masiva detecte duplicados en memoria (sin un SELECT por fila)."""
    query = """
        SELECT e.nombre
        FROM equipos e
        WHERE e.evaluacion_id = %s
        AND e.deleted_at IS NULL
    """
    filas = db.execute_query(query, (evaluacion_id,))
    return [fila["nombre"] for fila in filas] if filas else []

def reemplazar_equipo(
    id,
    curso_id,
    evaluacion_id,
    nombre
):
    query = """
        UPDATE equipos
        SET
            curso_id = %s,
            evaluacion_id = %s,
            nombre = %s
        WHERE id = %s
    """
    params = (
        curso_id,
        evaluacion_id,
        nombre,
        id
    )
    filas = db.execute_query(
        query,
        params,
        modifica_db=True
    )

    return filas > 0

def eliminar_equipo(id, hard=False):
    if hard:
        query = "DELETE FROM equipos WHERE id = %s"
    else:
        query = "UPDATE equipos SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s"
    filas_afectadas = db.execute_query(
        query,
        (id,),
        modifica_db=True
    )

    return filas_afectadas > 0