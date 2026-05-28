import db
from utils import paginacion


def obtener_estudiantes(
    carrera=None,
    anio_ingreso=None,
    activo=None,
    usuario_id=None,
    page_size=paginacion.PAGE_SIZE_DEFAULT,
    offset=0
):

    query = """
        SELECT
            e.id,
            e.usuario_id,
            e.padron,
            e.carrera,
            e.anio_ingreso,
            e.activo,
            e.created_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM estudiantes e
        INNER JOIN usuarios u ON u.id = e.usuario_id
        WHERE 1=1
    """
    params = []

    if carrera:
        query += " AND e.carrera LIKE %s"
        params.append(f"%{carrera}%")

    if anio_ingreso:
        query += " AND e.anio_ingreso = %s"
        params.append(anio_ingreso)

    if activo is not None:
        query += " AND e.activo = %s"
        params.append(activo)

    if usuario_id:
        query += " AND e.usuario_id = %s"
        params.append(usuario_id)

    return paginacion.ejecutar(
        query,
        params,
        order_by="e.id ASC",
        page_size=page_size,
        offset=offset,
    )


def crear_estudiante(usuario_id, padron, carrera, anio_ingreso):
    query = """
        INSERT INTO estudiantes
        (usuario_id, padron, carrera, anio_ingreso)
        VALUES (%s, %s, %s, %s)
    """

    params = (
        usuario_id,
        padron,
        carrera,
        anio_ingreso
    )

    new_id = db.execute_query(query, params, modifica_db=True)

    return obtener_estudiante_por_id(new_id)


def obtener_estudiante_por_id(id):
    query = """
        SELECT
            e.id,
            e.usuario_id,
            e.padron,
            e.carrera,
            e.anio_ingreso,
            e.activo,
            e.created_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM estudiantes e
        INNER JOIN usuarios u ON u.id = e.usuario_id
        WHERE e.id = %s
    """
    resultado = db.execute_query(query, (id,), un_solo_valor=True)
    return resultado


def obtener_estudiante_por_usuario_id(usuario_id):
    query = """
        SELECT
            e.id,
            e.usuario_id,
            e.padron,
            e.carrera,
            e.anio_ingreso,
            e.activo,
            e.created_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM estudiantes e
        INNER JOIN usuarios u ON u.id = e.usuario_id
        WHERE e.usuario_id = %s
    """
    resultado = db.execute_query(query, (usuario_id,), un_solo_valor=True)
    return resultado

def obtener_estudiante_por_padron(padron):
    query = """
        SELECT id, usuario_id, padron 
        FROM estudiantes 
        WHERE padron = %s AND activo = TRUE
    """
    return db.execute_query(query, (padron,), un_solo_valor=True)

def existe_padron(padron, excluir_id=None):
    if excluir_id is not None:
        query = "SELECT COUNT(*) as total FROM estudiantes WHERE padron = %s AND id != %s"
        result = db.execute_query(query, (padron, excluir_id), un_solo_valor=True)
    else:
        query = "SELECT COUNT(*) as total FROM estudiantes WHERE padron = %s"
        result = db.execute_query(query, (padron,), un_solo_valor=True)
    return result['total'] > 0 if result else False


def existe_estudiante_para_usuario(usuario_id):
    query = "SELECT COUNT(*) as total FROM estudiantes WHERE usuario_id = %s"
    result = db.execute_query(query, (usuario_id,), un_solo_valor=True)
    return result['total'] > 0 if result else False


def reemplazar_estudiante(id, padron, carrera, anio_ingreso, activo):
    query = """
        UPDATE estudiantes
        SET
            padron = %s,
            carrera = %s,
            anio_ingreso = %s,
            activo = %s
        WHERE id = %s
    """
    params = (
        padron,
        carrera,
        anio_ingreso,
        activo,
        id
    )
    filas = db.execute_query(
        query,
        params,
        modifica_db=True
    )

    return filas > 0


def modificar_estudiante_parcial(id, parametros):
    if not parametros:
        return obtener_estudiante_por_id(id)

    campos = []
    valores = []
    for columna, valor in parametros.items():
        campos.append(f"{columna} = %s")
        valores.append(valor)

    query = f"UPDATE estudiantes SET {', '.join(campos)} WHERE id = %s"
    valores.append(id)

    filas = db.execute_query(query, tuple(valores), modifica_db=True)
    if filas == 0:
        return None
    return obtener_estudiante_por_id(id)


def eliminar_estudiante(id: int):
    query = "UPDATE estudiantes SET activo = FALSE WHERE id = %s"
    filas_afectadas = db.execute_query(query, (id,), modifica_db=True)
    return filas_afectadas > 0
