import db
from utils import paginacion 

def obtener_todos(usuario_id=None, curso_id=None, estado=None, page_size=20, offset=0):
    query = """
        SELECT id, usuario_id, curso_id, estado 
        FROM curso_usuarios 
        WHERE 1=1
    """
    params = []

    if usuario_id is not None:
        query += " AND usuario_id = %s"
        params.append(usuario_id)
        
    if curso_id is not None:
        query += " AND curso_id = %s"
        params.append(curso_id)
        
    if estado is not None:
        query += " AND estado = %s"
        params.append(estado)

    return paginacion.ejecutar(query, params, "id ASC", page_size, offset)




def insertar(usuario_id, curso_id, estado):
    query = """
        INSERT INTO curso_usuarios (usuario_id, curso_id, estado)
        VALUES (%s, %s, %s)
    """
    
    nuevo_id = db.execute_query(query, (usuario_id, curso_id, estado), modifica_db=True)
    
    
    return obtener_por_id(nuevo_id)

def obtener_por_id(id):
    query = "SELECT id, usuario_id, curso_id, estado FROM curso_usuarios WHERE id = %s"
    return db.execute_query(query, (id,), un_solo_valor=True)


def existe_inscripcion(usuario_id, curso_id):
    query = "SELECT 1 FROM curso_usuarios WHERE usuario_id = %s AND curso_id = %s"
    resultado = db.execute_query(query, (usuario_id, curso_id), un_solo_valor=True)
    return resultado is not None



def actualizar(id, usuario_id, curso_id, estado):
    query = """
        UPDATE curso_usuarios 
        SET usuario_id = %s, curso_id = %s, estado = %s 
        WHERE id = %s
    """
    db.execute_query(query, (usuario_id, curso_id, estado, id), modifica_db=True)
    return obtener_por_id(id)


def eliminar(id):
    query = "DELETE FROM curso_usuarios WHERE id = %s"
    
    db.execute_query(query, (id,), modifica_db=True)