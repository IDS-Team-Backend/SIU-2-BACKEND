import db
from utils import paginacion


def obtener_estudiante_cursos(
    estudiante_id=None,
    curso_id=None,
    estado=None,
    page_size=paginacion.PAGE_SIZE_DEFAULT,
    offset=0
):

    query = """
        SELECT
            ec.id,
            ec.estudiante_id,
            ec.curso_id,
            ec.estado,
            ec.fecha_inscripcion,
            e.padron,
            e.carrera,
            e.anio_ingreso,
            u.nombre,
            u.apellido,
            u.email,
            u.dni,
            c.nombre AS curso_nombre
        FROM estudiante_curso ec
        INNER JOIN estudiantes e ON e.id = ec.estudiante_id
        INNER JOIN usuarios u ON u.id = e.usuario_id
        INNER JOIN cursos c ON c.id = ec.curso_id
        WHERE 1=1
    """
    params = []

    if estudiante_id:
        query += " AND ec.estudiante_id = %s"
        params.append(estudiante_id)

    if curso_id:
        query += " AND ec.curso_id = %s"
        params.append(curso_id)

    if estado is not None:
        query += " AND ec.estado = %s"
        params.append(estado)

    return paginacion.ejecutar(
        query,
        params,
        order_by="ec.id ASC",
        page_size=page_size,
        offset=offset,
    )


def crear_estudiante_curso(estudiante_id, curso_id, estado):
    query = """
        INSERT INTO estudiante_curso
        (estudiante_id, curso_id, estado)
        VALUES (%s, %s, %s)
    """

    params = (
        estudiante_id,
        curso_id,
        estado
    )

    new_id = db.execute_query(query, params, modifica_db=True)

    return obtener_estudiante_curso_por_id(new_id)


def obtener_estudiante_curso_por_id(id):
    query = """
        SELECT
            ec.id,
            ec.estudiante_id,
            ec.curso_id,
            ec.estado,
            ec.fecha_inscripcion,
            e.padron,
            e.carrera,
            e.anio_ingreso,
            u.nombre,
            u.apellido,
            u.email,
            u.dni,
            c.nombre AS curso_nombre
        FROM estudiante_curso ec
        INNER JOIN estudiantes e ON e.id = ec.estudiante_id
        INNER JOIN usuarios u ON u.id = e.usuario_id
        INNER JOIN cursos c ON c.id = ec.curso_id
        WHERE ec.id = %s
    """
    resultado = db.execute_query(query, (id,), un_solo_valor=True)
    return resultado


def obtener_estudiante_curso_por_estudiante_curso(estudiante_id, curso_id):
    query = """
        SELECT
            ec.id,
            ec.estudiante_id,
            ec.curso_id,
            ec.estado,
            ec.fecha_inscripcion
        FROM estudiante_curso ec
        WHERE ec.estudiante_id = %s AND ec.curso_id = %s
    """
    return db.execute_query(query, (estudiante_id, curso_id), un_solo_valor=True)


def existe_inscripcion(estudiante_id, curso_id, excluir_id=None):
    if excluir_id is not None:
        query = (
            "SELECT COUNT(*) as total FROM estudiante_curso "
            "WHERE estudiante_id = %s AND curso_id = %s AND id != %s"
        )
        result = db.execute_query(query, (estudiante_id, curso_id, excluir_id), un_solo_valor=True)
    else:
        query = (
            "SELECT COUNT(*) as total FROM estudiante_curso "
            "WHERE estudiante_id = %s AND curso_id = %s"
        )
        result = db.execute_query(query, (estudiante_id, curso_id), un_solo_valor=True)
    return result['total'] > 0 if result else False


def reemplazar_estudiante_curso(id, estudiante_id, curso_id, estado):
    query = """
        UPDATE estudiante_curso
        SET
            estudiante_id = %s,
            curso_id = %s,
            estado = %s
        WHERE id = %s
    """
    params = (
        estudiante_id,
        curso_id,
        estado,
        id
    )
    filas = db.execute_query(
        query,
        params,
        modifica_db=True
    )

    return filas > 0


def modificar_estudiante_curso_parcial(id, parametros):
    if not parametros:
        return obtener_estudiante_curso_por_id(id)

    campos = []
    valores = []
    for columna, valor in parametros.items():
        campos.append(f"{columna} = %s")
        valores.append(valor)

    query = f"UPDATE estudiante_curso SET {', '.join(campos)} WHERE id = %s"
    valores.append(id)

    filas = db.execute_query(query, tuple(valores), modifica_db=True)
    if filas == 0:
        return None
    return obtener_estudiante_curso_por_id(id)


def eliminar_estudiante_curso(id):
    query = "DELETE FROM estudiante_curso WHERE id = %s"
    filas_afectadas = db.execute_query(query, (id,), modifica_db=True)
    return filas_afectadas > 0
