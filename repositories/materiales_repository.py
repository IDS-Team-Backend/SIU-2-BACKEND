import db
from utils import paginacion


def obtener_todos(curso_id=None, subido_por=None, page_size=20, offset=0):
    query = """
        SELECT id, curso_id, titulo, archivo_url, subido_por, created_at
        FROM materiales
        WHERE deleted_at IS NULL
    """
    params = []

    if curso_id is not None:
        query += " AND curso_id = %s"
        params.append(curso_id)

    if subido_por is not None:
        query += " AND subido_por = %s"
        params.append(subido_por)

    return paginacion.ejecutar(query, params, "created_at DESC", page_size, offset)


def obtener_por_id(id):
    query = """
        SELECT id, curso_id, titulo, archivo_url, subido_por, created_at
        FROM materiales
        WHERE id = %s AND deleted_at IS NULL
    """
    return db.execute_query(query, (id,), un_solo_valor=True)


def insertar(curso_id, titulo, archivo_url, subido_por):
    query = """
        INSERT INTO materiales (curso_id, titulo, archivo_url, subido_por)
        VALUES (%s, %s, %s, %s)
    """
    nuevo_id = db.execute_query(
        query, (curso_id, titulo, archivo_url, subido_por), modifica_db=True
    )
    return obtener_por_id(nuevo_id)


def actualizar(id, curso_id, titulo, archivo_url, subido_por):
    query = """
        UPDATE materiales
        SET curso_id = %s, titulo = %s, archivo_url = %s, subido_por = %s
        WHERE id = %s
    """
    db.execute_query(query, (curso_id, titulo, archivo_url, subido_por, id), modifica_db=True)


def actualizar_parcial(id, data):
    campos_permitidos = ["curso_id", "titulo", "archivo_url", "subido_por"]

    set_clauses = []
    params = []

    for campo in campos_permitidos:
        if campo in data:
            set_clauses.append(f"{campo} = %s")
            params.append(data[campo])

    params.append(id)
    query = f"UPDATE materiales SET {', '.join(set_clauses)} WHERE id = %s"
    db.execute_query(query, params, modifica_db=True)


def eliminar(id, hard=False):
    if hard:
        query = "DELETE FROM materiales WHERE id = %s"
    else:
        query = "UPDATE materiales SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s"
        
    db.execute_query(query, (id,), modifica_db=True)
