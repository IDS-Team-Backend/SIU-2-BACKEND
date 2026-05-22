import db

def obtener_cursos(materia_id = None, nombre = None, anio = None, cuatrimestre = None):
    
    query = "FROM cursos c WHERE 1=1"
    params = []

    if materia_id:
        query += " AND c.materia_id = %s"
        params.append(materia_id)
    if nombre:
        query += " AND c.nombre LIKE %s"
        params.append(f"%{nombre}%")
    if anio:
        query += " AND c.anio = %s"
        params.append(anio)
    if cuatrimestre:    
        query += " AND c.cuatrimestre = %s"
        params.append(cuatrimestre)

    count_query = "SELECT COUNT(*) AS total " + query
    count_cursor = db.execute_query(count_query, tuple(params), un_solo_valor=True)

    total = count_cursor['total'] if count_cursor else 0

    select_query = "SELECT * " + query + " ORDER BY c.id"

    listado_cursos = db.execute_query(select_query, tuple(params))
    return listado_cursos, total

def crear_cursos(materia_id, nombre, anio, cuatrimestre):
    query = """
        INSERT INTO cursos (materia_id, nombre, anio, cuatrimestre)
        VALUES (%s, %s, %s, %s)
    """

    values = (
        materia_id,
        nombre,
        anio,
        cuatrimestre
    )

    nuevo_id = db.execute_query(query, values, modifica_db=True)
    return obtener_curso_por_id(nuevo_id)

def obtener_curso_por_id(curso_id):
    query = "SELECT * FROM cursos WHERE id = %s"
    return db.execute_query(query, (curso_id,), un_solo_valor=True)

def eliminar_curso(curso_id):
    query = "DELETE FROM cursos WHERE id = %s"

    db.execute_query(
        query,
        (curso_id,),
        modifica_db=True
    )

    return True

def remplazar_curso(curso_id, params):
    query = """
        UPDATE cursos
        SET materia_id = %s, nombre = %s, anio = %s, cuatrimestre = %s
        WHERE id = %s
    """

    values = (
        params['materia_id'],
        params['nombre'],
        params['anio'],
        params['cuatrimestre'],
        curso_id
    )

    filas_afectadas = db.execute_query(query, values, modifica_db=True)
    if filas_afectadas > 0:
        return obtener_curso_por_id(curso_id)
    return None

def existe_materia(materia_id):
    query = "SELECT 1 FROM materias WHERE id = %s"
    result = db.execute_query(query, (materia_id,), un_solo_valor=True)
    return result is not None

def existe_curso(materia_id, nombre, anio, cuatrimestre, excluir_id=None):
    query = """
        SELECT 1 FROM cursos
        WHERE materia_id = %s
          AND nombre = %s
          AND anio = %s
          AND cuatrimestre = %s
    """
    params = [materia_id, nombre, anio, cuatrimestre]
    if excluir_id is not None:
        query += " AND id != %s"
        params.append(excluir_id)

    result = db.execute_query(query, tuple(params), un_solo_valor=True)
    return result is not None