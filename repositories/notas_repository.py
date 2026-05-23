import db

def obtener_notas(evaluacion_id=None,alumno_id=None,equipo_id=None):
    query = """
        FROM notas n
        WHERE 1=1
    """
    params = []
    if evaluacion_id:
        query += " AND n.evaluacion_id = %s"
        params.append(evaluacion_id)
    if alumno_id:
        query += " AND n.alumno_id = %s"
        params.append(alumno_id)
    if equipo_id:
        query += " AND n.equipo_id = %s"
        params.append(equipo_id)
    count_query = """
        SELECT COUNT(*) as total
    """ + query
    count_notas = db.execute_query(
        count_query,
        tuple(params),
        un_solo_valor=True
    )
    total = (
        count_notas["total"]
        if count_notas
        else 0
    )
    select_query = """
        SELECT
            n.id,
            n.evaluacion_id,
            n.alumno_id,
            n.equipo_id,
            n.nota,
            n.observaciones,
            n.created_at
    """ + query + " ORDER BY n.id ASC"

    notas = db.execute_query(
        select_query,
        tuple(params)
    )

    return notas, total

def crear_nota_individual(evaluacion_id, alumno_id, nota, observaciones=None):
    query = """
        INSERT INTO notas
        (
            evaluacion_id,
            alumno_id,
            nota,
            observaciones
        )
        VALUES (%s, %s, %s, %s)
    """
    params = (
        evaluacion_id,
        alumno_id,
        nota,
        observaciones 
    )
    new_id = db.execute_query(
        query,
        params,
        modifica_db=True
    )
    return obtener_nota_por_id(new_id)

def crear_nota_grupal(evaluacion_id, equipo_id, nota, observaciones=None):
    query = """
        INSERT INTO notas
        (
            evaluacion_id,
            equipo_id,
            nota,
            observaciones
        )
        VALUES (%s, %s, %s, %s)
    """
    params = (
        evaluacion_id,
        equipo_id,
        nota,
        observaciones 
    )
    new_id = db.execute_query(
        query,
        params,
        modifica_db=True
    )

    return obtener_nota_por_id(new_id)

def obtener_nota_por_id(id):
    query = """
        SELECT
            n.id,
            n.evaluacion_id,
            n.alumno_id,
            n.equipo_id,
            n.nota,
            n.observaciones,
            n.created_at
        FROM notas n
        WHERE n.id = %s
    """
    return db.execute_query(
        query,
        (id,),
        un_solo_valor=True
    )

def reemplazar_nota(id,nota):
    query = """
        UPDATE notas
        SET nota = %s
        WHERE id = %s
    """
    filas = db.execute_query(
        query,
        (nota, id),
        modifica_db=True
    )
    return filas > 0

def eliminar_nota(id):
    query = """
        DELETE FROM notas
        WHERE id = %s
    """
    filas = db.execute_query(
        query,
        (id,),
        modifica_db=True
    )
    return filas > 0

def existe_nota_alumno(evaluacion_id,alumno_id):
    query = """
        SELECT COUNT(*) as total
        FROM notas
        WHERE evaluacion_id = %s
        AND alumno_id = %s
    """
    result = db.execute_query(
        query,
        (evaluacion_id, alumno_id),
        un_solo_valor=True
    )
    return result["total"] > 0 if result else False

def existe_nota_equipo(
    evaluacion_id,
    equipo_id
):
    query = """
        SELECT COUNT(*) as total
        FROM notas
        WHERE evaluacion_id = %s
        AND equipo_id = %s
    """
    result = db.execute_query(
        query,
        (evaluacion_id, equipo_id),
        un_solo_valor=True
    )

    return result["total"] > 0 if result else False