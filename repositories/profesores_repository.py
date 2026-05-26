import db
from utils import paginacion


def obtener_profesores(
    departamento=None,
    titulo=None,
    activo=None,
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
            p.activo,
            p.created_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM profesores p
        INNER JOIN usuarios u ON u.id = p.usuario_id
        WHERE 1=1
    """
    params = []

    if departamento:
        query += " AND p.departamento LIKE %s"
        params.append(f"%{departamento}%")

    if titulo:
        query += " AND p.titulo LIKE %s"
        params.append(f"%{titulo}%")

    if activo is not None:
        query += " AND p.activo = %s"
        params.append(activo)

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
            p.activo,
            p.created_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM profesores p
        INNER JOIN usuarios u ON u.id = p.usuario_id
        WHERE p.id = %s
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
            p.activo,
            p.created_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM profesores p
        INNER JOIN usuarios u ON u.id = p.usuario_id
        WHERE p.usuario_id = %s
    """
    return db.execute_query(query, (usuario_id,), un_solo_valor=True)


def existe_legajo(legajo, excluir_id=None):
    if excluir_id is not None:
        query = "SELECT COUNT(*) as total FROM profesores WHERE legajo = %s AND id != %s"
        result = db.execute_query(query, (legajo, excluir_id), un_solo_valor=True)
    else:
        query = "SELECT COUNT(*) as total FROM profesores WHERE legajo = %s"
        result = db.execute_query(query, (legajo,), un_solo_valor=True)
    return result['total'] > 0 if result else False


def existe_profesor_para_usuario(usuario_id):
    query = "SELECT COUNT(*) as total FROM profesores WHERE usuario_id = %s"
    result = db.execute_query(query, (usuario_id,), un_solo_valor=True)
    return result['total'] > 0 if result else False


def reemplazar_profesor(id, legajo, titulo, departamento, fecha_ingreso, activo):
    query = """
        UPDATE profesores
        SET
            legajo = %s,
            titulo = %s,
            departamento = %s,
            fecha_ingreso = %s,
            activo = %s
        WHERE id = %s
    """
    params = (legajo, titulo, departamento, fecha_ingreso, activo, id)
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


def eliminar_profesor(id: int):
    query = "UPDATE profesores SET activo = FALSE WHERE id = %s"
    filas_afectadas = db.execute_query(query, (id,), modifica_db=True)
    return filas_afectadas > 0
