import db

def obtener_alumnos_reporte(
    curso_id=None, 
    carrera=None, 
    anio_ingreso=None, 
    nombre_completo=None, 
    padron=None,
    evaluacion_id=None,
    condicion=None,
    nota_mayor_a=None
):
    query = """
        SELECT 
            e.id AS alumno_id,
            e.padron,
            e.carrera,
            e.anio_ingreso,
            u.nombre,
            u.apellido,
            u.email,
            u.dni,
            n.nota AS nota_evaluacion
        FROM estudiantes e
        INNER JOIN usuarios u ON e.usuario_id = u.id
        LEFT JOIN curso_usuarios cu ON u.id = cu.usuario_id
        LEFT JOIN notas n ON e.id = n.alumno_id
        WHERE e.activo = TRUE
    """
    params = []
    
    # filtros estructurales
    if curso_id:
        query += " AND cu.curso_id = %s AND cu.estado = 'activo'"
        params.append(curso_id)
    if carrera:
        query += " AND e.carrera = %s"
        params.append(carrera)
    if anio_ingreso:
        query += " AND e.anio_ingreso = %s"
        params.append(anio_ingreso)
    if nombre_completo:
        query += " AND (u.nombre LIKE %s OR u.apellido LIKE %s)"
        termino = f"%{nombre_completo}%"
        params.append(termino)
        params.append(termino)
    if padron:
        query += " AND e.padron = %s"
        params.append(padron)
        
    # filtros académicos
    if evaluacion_id:
        query += " AND n.evaluacion_id = %s"
        params.append(evaluacion_id)
    if condicion:
        condicion_limpia = condicion.lower()
        if condicion_limpia == "aprobado":
            query += " AND n.nota >= 4.0"
        elif condicion_limpia == "desaprobado":
            query += " AND n.nota < 4.0"
    if nota_mayor_a:
        query += " AND n.nota > %s"
        params.append(float(nota_mayor_a))

    query += """ 
        GROUP BY 
            e.id, 
            e.padron, 
            e.carrera, 
            e.anio_ingreso, 
            u.nombre, 
            u.apellido, 
            u.email, 
            u.dni, 
            n.nota 
        ORDER BY u.apellido ASC, u.nombre ASC
    """
    
    return db.execute_query(query, tuple(params))


def obtener_estadisticas_aprobacion(curso_id):
    query = """
        SELECT 
            ev.id AS evaluacion_id,
            ev.titulo AS evaluacion_titulo,
            te.nombre AS tipo_evaluacion,
            COUNT(n.id) AS total_notas,
            SUM(CASE WHEN n.nota >= 4 THEN 1 ELSE 0 END) AS aprobados,
            SUM(CASE WHEN n.nota < 4 THEN 1 ELSE 0 END) AS desaprobados,
            ROUND(AVG(n.nota), 2) AS nota_promedio
        FROM evaluaciones ev
        INNER JOIN tipos_evaluacion te ON ev.tipo_evaluacion_id = te.id
        LEFT JOIN notas n ON ev.id = n.evaluacion_id
        WHERE ev.curso_id = %s AND ev.activo = TRUE
        GROUP BY ev.id, ev.titulo, te.nombre
        ORDER BY ev.fecha ASC
    """
    return db.execute_query(query, (curso_id,))


def obtener_equipos_reporte(curso_id):
    query = """
        SELECT 
            eq.id AS equipo_id,
            eq.nombre AS equipo_nombre,
            ev.titulo AS evaluacion_contexto,
            GROUP_CONCAT(CONCAT(u.apellido, ', ', u.nombre, ' (Padrón: ', e.padron, ')') SEPARATOR ' | ') AS integrantes
        FROM equipos eq
        INNER JOIN evaluaciones ev ON eq.evaluacion_id = ev.id
        LEFT JOIN equipo_integrantes ei ON eq.id = ei.equipo_id
        LEFT JOIN estudiantes e ON ei.alumno_id = e.id
        LEFT JOIN usuarios u ON e.usuario_id = u.id
        WHERE eq.curso_id = %s AND eq.activo = TRUE
        GROUP BY eq.id, eq.nombre, ev.titulo
        ORDER BY eq.nombre ASC
    """
    return db.execute_query(query, (curso_id,))