import db

def get_clases(filtros):
    if 'activa' in filtros and filtros['activa'] is False:
        query_base = " FROM clases WHERE 1=1 AND deleted_at IS NOT NULL"
    else:
        query_base = " FROM clases WHERE 1=1 AND deleted_at IS NULL"
        
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
        query_base += " AND DATE(fecha_hora_inicio) = %s"
        params.append(filtros['fecha'])

    query_clases = "SELECT *" + query_base + " ORDER BY fecha_hora_inicio DESC"
    clases = db.execute_query(query_clases, tuple(params))

    query_count = "SELECT COUNT(*) as total" + query_base
    count_result = db.execute_query(query_count, tuple(params), un_solo_valor=True)
    
    total = count_result['total'] if count_result else 0

    return clases, total

def get_clase_by_id(clase_id, incluir_eliminadas=False):
    query = "SELECT * FROM clases WHERE id = %s"
    params = [clase_id]

    if not incluir_eliminadas:
        query += " AND deleted_at IS NULL"

    clase = db.execute_query(query, tuple(params), un_solo_valor=True)

    return clase

def crear_clase(nombre, profesor_id, curso_id, fecha_hora_inicio, fecha_hora_fin, tema=None, status="pendiente"):
    query = """
    INSERT INTO clases (
        nombre,
        profesor_id,
        curso_id,
        fecha_hora_inicio,
        fecha_hora_fin,
        tema,
        status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (nombre, profesor_id, curso_id, fecha_hora_inicio, fecha_hora_fin, tema, status)
    
    new_clase_id = db.execute_query(query, params, modifica_db=True)
    
    return get_clase_by_id(new_clase_id)

def actualizar_clase(clase_id, nombre, profesor_id, curso_id, fecha_hora_inicio, fecha_hora_fin, tema=None, status="pendiente"):
    query = """
    UPDATE clases SET
        nombre = %s,
        profesor_id = %s,
        curso_id = %s,
        fecha_hora_inicio = %s,
        fecha_hora_fin = %s,
        tema = %s,
        status = %s
    WHERE id = %s
    """
    params = (nombre, profesor_id, curso_id, fecha_hora_inicio, fecha_hora_fin, tema, status, clase_id)
    
    db.execute_query(query, params, modifica_db=True)
    
    return get_clase_by_id(clase_id)

def eliminar_clase(clase_id): # esto es un soft delete, con delete_at = datetime. mucho mejor que un boolean 
    query = "UPDATE clases SET deleted_at = NOW() WHERE id = %s"
    db.execute_query(query, (clase_id,), modifica_db=True)

def buscar_clase_superpuesta(profesor_id, fecha_hora_inicio, fecha_hora_fin, clase_id=None):
    query = """
        SELECT id, nombre, fecha_hora_inicio, fecha_hora_fin 
        FROM clases 
        WHERE profesor_id = %s 
        AND deleted_at IS NULL 
        AND status != 'suspendida'
        AND (%s < fecha_hora_fin AND %s > fecha_hora_inicio)
    """
    params = [profesor_id, fecha_hora_inicio, fecha_hora_fin]
    
    # en caso de que estamos editando una clase, no la debemos comparar con esa misma clase 
    if clase_id:
        query += " AND id != %s"
        params.append(clase_id)

    query += " LIMIT 1" # solo nos importa que haya 1 clase superpuesta
    
    return db.execute_query(query, tuple(params), un_solo_valor=True)

# repositories/clases_repository.py

def actualizar_clase_parcial(clase_id, parametros):
    if not parametros:
        return get_clase_by_id(clase_id)

    campos = []
    valores = []

    # query dinamica en base a los campos 
    for columna, valor in parametros.items():
        campos.append(f"{columna} = %s")
        valores.append(valor)

    # unimos los campos con comas (' "nombre = %s, status = %s" ')
    clausula_set = ", ".join(campos)

    query = f"""
        UPDATE clases 
        SET {clausula_set} 
        WHERE id = %s AND deleted_at IS NULL
    """
    valores.append(clase_id)

    db.execute_query(query, tuple(valores), modifica_db=True)

    return get_clase_by_id(clase_id)