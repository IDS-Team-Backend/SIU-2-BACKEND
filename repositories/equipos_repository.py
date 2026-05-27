import db

def obtener_equipos(
    curso_id=None,
    evaluacion_id=None,
    nombre=None,
    activo=None
):
    query = """
        FROM equipos e
        WHERE 1=1
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
    if activo is not None:
        query += " AND e.activo = %s"
        params.append(activo.lower() == "true")
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
            e.activo,
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
            e.activo,
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

def reemplazar_equipo(
    id,
    curso_id,
    evaluacion_id,
    nombre,
    activo
):
    query = """
        UPDATE equipos
        SET
            curso_id = %s,
            evaluacion_id = %s,
            nombre = %s,
            activo = %s
        WHERE id = %s
    """
    params = (
        curso_id,
        evaluacion_id,
        nombre,
        activo,
        id
    )
    filas = db.execute_query(
        query,
        params,
        modifica_db=True
    )

    return filas > 0

def eliminar_equipo(id):
    query = """
        UPDATE equipos
        SET activo = FALSE
        WHERE id = %s
    """
    filas_afectadas = db.execute_query(
        query,
        (id,),
        modifica_db=True
    )

    return filas_afectadas > 0