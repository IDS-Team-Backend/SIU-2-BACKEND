import db


def crear(usuario_id, codigo_hash, expira):
    query = """
        INSERT INTO verificacion_registro (usuario_id, codigo, expira)
        VALUES (%s, %s, %s)
    """
    return db.execute_query(query, (usuario_id, codigo_hash, expira), modifica_db=True)


def obtener_vigente_por_usuario(usuario_id):
    """Devuelve la verificación más reciente sin consumir y no expirada, o None."""
    query = """
        SELECT id, usuario_id, codigo, expira, consumido_at, created_at
        FROM verificacion_registro
        WHERE usuario_id = %s
          AND consumido_at IS NULL
          AND expira > NOW()
        ORDER BY id DESC
        LIMIT 1
    """
    return db.execute_query(query, (usuario_id,), un_solo_valor=True)


def marcar_consumido(id):
    query = "UPDATE verificacion_registro SET consumido_at = NOW() WHERE id = %s"
    db.execute_query(query, (id,), modifica_db=True)
