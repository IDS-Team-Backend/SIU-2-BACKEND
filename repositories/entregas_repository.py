import db

CAMPOS_ACTUALIZABLES = [
    "fecha_entrega",
    "estado",
    "archivo_url",
    "observaciones",
]

def obtener_entregas(evaluacion_id=None, alumno_id=None, equipo_id=None):
    query = """
        FROM entregas e
        WHERE 1=1
    """
    params = []
    if evaluacion_id:
        query += " AND e.evaluacion_id = %s"
        params.append(evaluacion_id)
    if alumno_id:
        query += " AND e.alumno_id = %s"
        params.append(alumno_id)
    if equipo_id:
        query += " AND e.equipo_id = %s"
        params.append(equipo_id)
    count_query = """
        SELECT COUNT(*) as total
    """ + query
    count_entregas = db.execute_query(
        count_query,
        tuple(params),
        un_solo_valor=True
    )
    total = (
        count_entregas["total"]
        if count_entregas
        else 0
    )
    select_query = """
        SELECT
            e.id,
            e.evaluacion_id,
            e.alumno_id,
            e.equipo_id,
            e.fecha_entrega,
            e.estado,
            e.archivo_url,
            e.observaciones,
            e.created_at
    """ + query + " ORDER BY e.id ASC"

    entregas = db.execute_query(
        select_query,
        tuple(params)
    )

    return entregas, total

def crear_entrega_individual(evaluacion_id, alumno_id, fecha_entrega, estado, archivo_url=None, observaciones=None):
    query = """
        INSERT INTO entregas
        (
            evaluacion_id,
            alumno_id,
            fecha_entrega,
            estado,
            archivo_url,
            observaciones
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (
        evaluacion_id,
        alumno_id,
        fecha_entrega,
        estado,
        archivo_url,
        observaciones
    )
    new_id = db.execute_query(
        query,
        params,
        modifica_db=True
    )
    return obtener_entrega_por_id(new_id)

def crear_entrega_grupal(evaluacion_id, equipo_id, fecha_entrega, estado, archivo_url=None, observaciones=None):
    query = """
        INSERT INTO entregas
        (
            evaluacion_id,
            equipo_id,
            fecha_entrega,
            estado,
            archivo_url,
            observaciones
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (
        evaluacion_id,
        equipo_id,
        fecha_entrega,
        estado,
        archivo_url,
        observaciones
    )
    new_id = db.execute_query(
        query,
        params,
        modifica_db=True
    )

    return obtener_entrega_por_id(new_id)

def obtener_entrega_por_id(id):
    query = """
        SELECT
            e.id,
            e.evaluacion_id,
            e.alumno_id,
            e.equipo_id,
            e.fecha_entrega,
            e.estado,
            e.archivo_url,
            e.observaciones,
            e.created_at
        FROM entregas e
        WHERE e.id = %s
    """
    return db.execute_query(
        query,
        (id,),
        un_solo_valor=True
    )

def actualizar_entrega(id, campos):
    set_clauses = []
    params = []
    for campo in CAMPOS_ACTUALIZABLES:
        if campo in campos:
            set_clauses.append(f"{campo} = %s")
            params.append(campos[campo])

    if not set_clauses:
        return False

    params.append(id)
    query = f"""
        UPDATE entregas
        SET {", ".join(set_clauses)}
        WHERE id = %s
    """
    filas = db.execute_query(
        query,
        tuple(params),
        modifica_db=True
    )
    return filas > 0

def eliminar_entrega(id):
    query = """
        DELETE FROM entregas
        WHERE id = %s
    """
    filas = db.execute_query(
        query,
        (id,),
        modifica_db=True
    )
    return filas > 0

def existe_entrega_alumno(evaluacion_id, alumno_id):
    query = """
        SELECT COUNT(*) as total
        FROM entregas
        WHERE evaluacion_id = %s
        AND alumno_id = %s
    """
    result = db.execute_query(
        query,
        (evaluacion_id, alumno_id),
        un_solo_valor=True
    )
    return result["total"] > 0 if result else False

def existe_entrega_equipo(evaluacion_id, equipo_id):
    query = """
        SELECT COUNT(*) as total
        FROM entregas
        WHERE evaluacion_id = %s
        AND equipo_id = %s
    """
    result = db.execute_query(
        query,
        (evaluacion_id, equipo_id),
        un_solo_valor=True
    )

    return result["total"] > 0 if result else False
