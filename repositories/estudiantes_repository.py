import db
from utils import paginacion


def obtener_estudiantes(
    carrera=None,
    anio_ingreso=None,
    usuario_id=None,
    q=None,
    eliminados=False,
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
            e.created_at,
            e.deleted_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM estudiantes e
        INNER JOIN usuarios u ON u.id = e.usuario_id
        WHERE e.deleted_at IS """ + ("NOT NULL" if eliminados else "NULL") + """
    """
    params = []

    if carrera:
        query += " AND e.carrera LIKE %s"
        params.append(f"%{carrera}%")

    if anio_ingreso:
        query += " AND e.anio_ingreso = %s"
        params.append(anio_ingreso)

    if usuario_id:
        query += " AND e.usuario_id = %s"
        params.append(usuario_id)

    if q:
        query += """ AND (
            u.nombre LIKE %s
            OR u.apellido LIKE %s
            OR u.email LIKE %s
            OR CAST(u.dni AS CHAR) LIKE %s
            OR CAST(e.padron AS CHAR) LIKE %s
        )"""
        comodin = f"%{q}%"
        params.extend([comodin, comodin, comodin, comodin, comodin])

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
            e.created_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM estudiantes e
        INNER JOIN usuarios u ON u.id = e.usuario_id
        WHERE e.id = %s AND e.deleted_at IS NULL
    """
    return db.execute_query(query, (id,), un_solo_valor=True)


def obtener_estudiante_por_usuario_id(usuario_id):
    query = """
        SELECT
            e.id,
            e.usuario_id,
            e.padron,
            e.carrera,
            e.anio_ingreso,
            e.created_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM estudiantes e
        INNER JOIN usuarios u ON u.id = e.usuario_id
        WHERE e.usuario_id = %s AND e.deleted_at IS NULL
    """
    return db.execute_query(query, (usuario_id,), un_solo_valor=True)


def obtener_estudiante_por_padron(padron):
    query = """
        SELECT
            e.id,
            e.usuario_id,
            e.padron,
            e.carrera,
            e.anio_ingreso,
            e.created_at,
            u.nombre,
            u.apellido,
            u.email,
            u.dni
        FROM estudiantes e
        INNER JOIN usuarios u ON u.id = e.usuario_id
        WHERE e.padron = %s AND e.deleted_at IS NULL
    """
    return db.execute_query(query, (padron,), un_solo_valor=True)


def obtener_estudiantes_por_padrones(padrones):
    """Resuelve varios padrones de una sola vez (SELECT ... IN). Devuelve los
    estudiantes activos encontrados; los padrones inexistentes simplemente no vienen.
    """
    if not padrones:
        return []
    placeholders = ", ".join(["%s"] * len(padrones))
    query = f"""
        SELECT e.id, e.padron
        FROM estudiantes e
        WHERE e.padron IN ({placeholders})
        AND e.activo = TRUE
    """
    return db.execute_query(query, tuple(padrones)) or []


def existe_padron(padron, excluir_id=None):
    if excluir_id is not None:
        query = "SELECT COUNT(*) as total FROM estudiantes WHERE padron = %s AND id != %s AND deleted_at IS NULL"
        result = db.execute_query(query, (padron, excluir_id), un_solo_valor=True)
    else:
        query = "SELECT COUNT(*) as total FROM estudiantes WHERE padron = %s AND deleted_at IS NULL"
        result = db.execute_query(query, (padron,), un_solo_valor=True)
    return result['total'] > 0 if result else False


def existe_estudiante_para_usuario(usuario_id):
    query = "SELECT COUNT(*) as total FROM estudiantes WHERE usuario_id = %s AND deleted_at IS NULL"
    result = db.execute_query(query, (usuario_id,), un_solo_valor=True)
    return result['total'] > 0 if result else False


def reemplazar_estudiante(id, padron, carrera, anio_ingreso):
    query = """
        UPDATE estudiantes
        SET
            padron = %s,
            carrera = %s,
            anio_ingreso = %s
        WHERE id = %s
    """
    params = (
        padron,
        carrera,
        anio_ingreso,
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

    db.execute_query(query, tuple(valores), modifica_db=True)
    return obtener_estudiante_por_id(id)


def eliminar_estudiante(id: int, hard=False):
    if hard:
        query = "DELETE FROM estudiantes WHERE id = %s"
    else:
        query = "UPDATE estudiantes SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s"
    filas_afectadas = db.execute_query(query, (id,), modifica_db=True)
    return filas_afectadas > 0


def reactivar_estudiante(id: int):
    query = "UPDATE estudiantes SET deleted_at = NULL WHERE id = %s AND deleted_at IS NOT NULL"
    filas_afectadas = db.execute_query(query, (id,), modifica_db=True)
    return filas_afectadas > 0



def eliminar_estudiantes_lote(ids):
    """Baja masiva (soft-delete) por lote de ids de estudiante.
    Un solo for sobre la misma conexión, igual al patrón usado en
    estudiante_curso_repository para las operaciones por lote."""
    eliminados = 0
    errores = []

    for est_id in ids:
        try:
            est_id = int(est_id)
        except (ValueError, TypeError):
            errores.append({"estudiante_id": est_id, "error": "id inválido"})
            continue

        if eliminar_estudiante(est_id, hard=False):
            eliminados += 1
        else:
            errores.append({"estudiante_id": est_id, "error": "estudiante inexistente"})

    return eliminados, errores


def reactivar_estudiantes_lote(ids):
    reactivados = 0
    errores = []

    for est_id in ids:
        try:
            est_id = int(est_id)
        except (ValueError, TypeError):
            errores.append({"estudiante_id": est_id, "error": "id inválido"})
            continue

        if reactivar_estudiante(est_id):
            reactivados += 1
        else:
            errores.append({"estudiante_id": est_id, "error": "estudiante inexistente o no eliminado"})

    return reactivados, errores
