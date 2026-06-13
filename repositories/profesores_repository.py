import db
from utils import paginacion


def obtener_profesores(
    departamento=None,
    titulo=None,
    usuario_id=None,
    page_size=paginacion.PAGE_SIZE_DEFAULT,
    offset=0,
):

    query = """
        SELECT
            p.id,
            p.usuario_id,
            p.legajo,
            p.titulo,
            p.departamento,
            p.fecha_ingreso,
            p.created_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM profesores p
        INNER JOIN usuarios u ON u.id = p.usuario_id
        WHERE p.deleted_at IS NULL
    """
    params = []

    if departamento:
        query += " AND p.departamento LIKE %s"
        params.append(f"%{departamento}%")

    if titulo:
        query += " AND p.titulo LIKE %s"
        params.append(f"%{titulo}%")

    if usuario_id:
        query += " AND p.usuario_id = %s"
        params.append(usuario_id)

    return paginacion.ejecutar(
        query,
        params,
        order_by="p.id ASC",
        page_size=page_size,
        offset=offset,
    )


def crear_profesor(usuario_id, legajo, titulo, departamento, fecha_ingreso):
    query = """
        INSERT INTO profesores
        (usuario_id, legajo, titulo, departamento, fecha_ingreso)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (usuario_id, legajo, titulo, departamento, fecha_ingreso)
    new_id = db.execute_query(query, params, modifica_db=True)
    return obtener_profesor_por_id(new_id)


def obtener_profesor_por_id(id):
    query = """
        SELECT
            p.id,
            p.usuario_id,
            p.legajo,
            p.titulo,
            p.departamento,
            p.fecha_ingreso,
            p.created_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM profesores p
        INNER JOIN usuarios u ON u.id = p.usuario_id
        WHERE p.id = %s AND p.deleted_at IS NULL
    """
    return db.execute_query(query, (id,), un_solo_valor=True)


def obtener_profesor_por_usuario_id(usuario_id):
    query = """
        SELECT
            p.id,
            p.usuario_id,
            p.legajo,
            p.titulo,
            p.departamento,
            p.fecha_ingreso,
            p.created_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM profesores p
        INNER JOIN usuarios u ON u.id = p.usuario_id
        WHERE p.usuario_id = %s AND p.deleted_at IS NULL
    """
    return db.execute_query(query, (usuario_id,), un_solo_valor=True)

def obtener_profesor_por_legajo(legajo):
    query = """
        SELECT
            p.id,
            p.usuario_id,
            p.legajo,
            p.titulo,
            p.departamento,
            p.fecha_ingreso,
            p.deleted_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM profesores p
        INNER JOIN usuarios u ON u.id = p.usuario_id
        WHERE p.legajo = %s
    """
    return db.execute_query(query, (legajo,), un_solo_valor=True)


def existe_legajo(legajo, excluir_id=None):
    if excluir_id is not None:
        query = "SELECT COUNT(*) as total FROM profesores WHERE legajo = %s AND id != %s AND deleted_at IS NULL"
        result = db.execute_query(query, (legajo, excluir_id), un_solo_valor=True)
    else:
        query = "SELECT COUNT(*) as total FROM profesores WHERE legajo = %s AND deleted_at IS NULL"
        result = db.execute_query(query, (legajo,), un_solo_valor=True)
    return result['total'] > 0 if result else False


def existe_profesor_para_usuario(usuario_id):
    query = "SELECT COUNT(*) as total FROM profesores WHERE usuario_id = %s AND deleted_at IS NULL"
    result = db.execute_query(query, (usuario_id,), un_solo_valor=True)
    return result['total'] > 0 if result else False


def reemplazar_profesor(id, legajo, titulo, departamento, fecha_ingreso):
    query = """
        UPDATE profesores
        SET
            legajo = %s,
            titulo = %s,
            departamento = %s,
            fecha_ingreso = %s,
        WHERE id = %s
    """
    params = (legajo, titulo, departamento, fecha_ingreso, id)
    filas = db.execute_query(query, params, modifica_db=True)
    return filas > 0


def modificar_profesor_parcial(id, parametros):
    if not parametros:
        return obtener_profesor_por_id(id)

    campos = []
    valores = []
    for columna, valor in parametros.items():
        campos.append(f"{columna} = %s")
        valores.append(valor)

    query = f"UPDATE profesores SET {', '.join(campos)} WHERE id = %s"
    valores.append(id)

    filas = db.execute_query(query, tuple(valores), modifica_db=True)
    if filas == 0:
        return None
    return obtener_profesor_por_id(id)


def eliminar_profesor(id: int, hard=False):
    if hard:
        query = "DELETE FROM usuarios WHERE id = %s"
    else:
        query = "UPDATE usuarios SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s"
    filas_afectadas = db.execute_query(query, (id,), modifica_db=True)
    return filas_afectadas > 0
