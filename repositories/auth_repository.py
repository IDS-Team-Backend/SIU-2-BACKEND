import db

def obtener_usuario_completo(usuario_id):
    """
    devuelve el usuario y, si existen, sus IDs de profesor y alumno en una sola consulta.
    """
    query = """
        SELECT 
            u.id, u.nombre, u.email,
            p.id AS profesor_id,
            e.id AS alumno_id
        FROM usuarios u
        LEFT JOIN profesores p ON u.id = p.usuario_id
        LEFT JOIN estudiantes e ON u.id = e.usuario_id
        WHERE u.id = %s
    """
    
    usuario = db.execute_query(query, (usuario_id,), un_solo_valor=True)
    
    return usuario