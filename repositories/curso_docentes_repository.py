import db


def docente_pertenece_activamente_a_curso(docente_id, curso_id):
    query = """
        SELECT 1
        FROM curso_docentes
        WHERE docente_id = %s
          AND curso_id = %s
        LIMIT 1
    """
    resultado = db.execute_query(query, (docente_id, curso_id), un_solo_valor=True)
    return resultado is not None