# repositories/tipos_evaluacion_repository.py

from db import execute_query


def obtener_tipos_evaluacion():
    query = """
        SELECT
            id,
            nombre,
            es_grupal
        FROM tipos_evaluacion
        ORDER BY nombre
    """

    return execute_query(query, ())


def obtener_tipo_evaluacion_por_id(tipo_evaluacion_id):
    query = """
        SELECT
            id,
            nombre,
            es_grupal
        FROM tipos_evaluacion
        WHERE id = %s
    """

    return execute_query(
        query,
        (tipo_evaluacion_id,),
        un_solo_valor=True
    )


def crear_tipo_evaluacion(nombre, es_grupal):
    query = """
        INSERT INTO tipos_evaluacion
        (
            nombre,
            es_grupal
        )
        VALUES
        (
            %s,
            %s
        )
    """

    return execute_query(
        query,
        (nombre, es_grupal),
        modifica_db=True
    )


def actualizar_tipo_evaluacion(
    tipo_evaluacion_id,
    nombre,
    es_grupal
):
    query = """
        UPDATE tipos_evaluacion
        SET
            nombre = %s,
            es_grupal = %s
        WHERE id = %s
    """

    return execute_query(
        query,
        (nombre, es_grupal, tipo_evaluacion_id),
        modifica_db=True
    )


def eliminar_tipo_evaluacion(tipo_evaluacion_id):
    query = """
        DELETE FROM tipos_evaluacion
        WHERE id = %s
    """

    return execute_query(
        query,
        (tipo_evaluacion_id,),
        modifica_db=True
    )