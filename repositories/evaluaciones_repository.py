import db


def obtener_evaluaciones(
    curso_id=None,
    tipo_evaluacion_id=None,
    titulo=None,
    fecha=None,
    activo=None
):
    query = """
        FROM evaluaciones e
        WHERE 1=1
    """
    params = []
    if curso_id:
        query += " AND e.curso_id = %s"
        params.append(curso_id)
    if tipo_evaluacion_id:
        query += " AND e.tipo_evaluacion_id = %s"
        params.append(tipo_evaluacion_id)
    if titulo:
        query += " AND e.titulo LIKE %s"
        params.append(f"%{titulo}%")
    if fecha:
        query += " AND e.fecha = %s"
        params.append(fecha)
    if activo is not None:
        query += " AND e.activo = %s"
        params.append(activo.lower() == "true")
    count_query = """
        SELECT COUNT(*) as total
    """ + query
    count_evaluaciones = db.execute_query(
        count_query,
        tuple(params),
        un_solo_valor=True
    )
    total = (
        count_evaluaciones["total"]
        if count_evaluaciones
        else 0
    )
    select_query = """
        SELECT
            e.id,
            e.curso_id,
            e.tipo_evaluacion_id,
            e.titulo,
            e.descripcion,
            e.fecha,
            e.activo,
            e.created_at
    """ + query + " ORDER BY e.id ASC"
    lista_evaluaciones = db.execute_query(
        select_query,
        tuple(params)
    )
    return lista_evaluaciones, total


def crear_evaluacion(
    curso_id,
    tipo_evaluacion_id,
    titulo,
    descripcion,
    fecha
):
    query = """
        INSERT INTO evaluaciones
        (
            curso_id,
            tipo_evaluacion_id,
            titulo,
            descripcion,
            fecha
        )
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (
        curso_id,
        tipo_evaluacion_id,
        titulo,
        descripcion,
        fecha
    )
    new_id = db.execute_query(
        query,
        params,
        modifica_db=True
    )
    return obtener_evaluacion_por_id(new_id)


def obtener_evaluacion_por_id(id):
    query = """
        SELECT
            e.id,
            e.curso_id,
            e.tipo_evaluacion_id,
            e.titulo,
            e.descripcion,
            e.fecha,
            e.activo,
            e.created_at,
            te.es_grupal,
            te.nombre as tipo_evaluacion
        FROM evaluaciones e
        INNER JOIN tipos_evaluacion te
            ON te.id = e.tipo_evaluacion_id
        WHERE e.id = %s
    """
    resultado = db.execute_query(
        query,
        (id,),
        un_solo_valor=True
    )
    return resultado

def reemplazar_evaluacion(
    id,
    curso_id,
    tipo_evaluacion_id,
    titulo,
    descripcion,
    fecha,
    activo
):
    query = """
        UPDATE evaluaciones
        SET
            curso_id = %s,
            tipo_evaluacion_id = %s,
            titulo = %s,
            descripcion = %s,
            fecha = %s,
            activo = %s
        WHERE id = %s
    """
    params = (
        curso_id,
        tipo_evaluacion_id,
        titulo,
        descripcion,
        fecha,
        activo,
        id
    )
    filas = db.execute_query(
        query,
        params,
        modifica_db=True
    )
    return filas > 0

def eliminar_evaluacion(id):
    query = """
        UPDATE evaluaciones
        SET activo = FALSE
        WHERE id = %s
    """
    filas_afectadas = db.execute_query(
        query,
        (id,),
        modifica_db=True
    )
    return filas_afectadas > 0