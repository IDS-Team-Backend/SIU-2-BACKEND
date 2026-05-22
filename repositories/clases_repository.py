import db

def get_clases(filtros):
    query_base = " FROM clases WHERE 1=1"
    params = []
    
    if 'status' in filtros:
        query_base += " AND status = %s"
        params.append(filtros['status'])
        
    if 'profesor_id' in filtros:
        query_base += " AND profesor_id = %s"
        params.append(filtros['profesor_id'])
        
    if 'curso_id' in filtros:
        query_base += " AND curso_id = %s"
        params.append(filtros['curso_id'])
        
    if 'fecha' in filtros:
        query_base += " AND DATE(fecha_hora) = %s"
        params.append(filtros['fecha'])

    query_clases = "SELECT *" + query_base + " ORDER BY fecha_hora DESC"
    clases = db.execute_query(query_clases, tuple(params))

    query_count = "SELECT COUNT(*) as total" + query_base
    count_result = db.execute_query(query_count, tuple(params), un_solo_valor=True)
    
    total = count_result['total'] if count_result else 0

    return clases, total

def get_clase_by_id(clase_id):
    query = "SELECT * FROM clases WHERE id = %s"
    clase = db.execute_query(query, (clase_id,), un_solo_valor=True)

    return clase