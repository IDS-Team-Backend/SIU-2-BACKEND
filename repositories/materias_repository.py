import db
from utils import paginacion

def obtener_materias(nombre=None, codigo=None, page_size=20, offset=0):
    query = """
        SELECT m.id, m.nombre, m.codigo
        FROM materias m
        WHERE 1=1
    """
    params = []

    if nombre:
        query += " AND m.nombre LIKE %s"
        params.append(f"%{nombre}%")

    if codigo:
        query += " AND m.codigo = %s"
        params.append(codigo)

    return paginacion.ejecutar(query, params, "id ASC", page_size, offset)

def crear_materia(nombre, codigo):
    query = """
        INSERT INTO materias (nombre, codigo)
        VALUES (%s, %s)
    """
    values = (nombre.strip(), codigo.strip() if codigo else None)
    nuevo_id = db.execute_query(query, values, modifica_db=True)
    return obtener_materia_por_id(nuevo_id)

def obtener_materia_por_id(materia_id):
    query = "SELECT * FROM materias WHERE id = %s"
    return db.execute_query(query, (materia_id,), un_solo_valor=True)

def eliminar_materia(materia_id):
    query = "DELETE FROM materias WHERE id = %s"
    db.execute_query(query, (materia_id,), modifica_db=True)
    return True

def reemplazar_materia(materia_id, params):
    query = """
        UPDATE materias
        SET nombre = %s, codigo = %s
        WHERE id = %s
    """
    values = (
        params["nombre"].strip(),
        params["codigo"].strip() if params.get("codigo") else None,
        materia_id
    )
    db.execute_query(query, values, modifica_db=True)
    return obtener_materia_por_id(materia_id)

def existe_codigo(codigo, excluir_id=None):
    if excluir_id is not None:
        query = """
            SELECT COUNT(*) as total
            FROM materias
            WHERE codigo = %s
              AND id != %s
        """
        params = (codigo.strip(), excluir_id)
    else:
        query = """
            SELECT COUNT(*) as total
            FROM materias
            WHERE codigo = %s
        """
        params = (codigo.strip(),)

    result = db.execute_query(query, params, un_solo_valor=True)
    return result["total"] > 0 if result else False

def obtener_cursos_de_materia(materia_id, page_size=20, offset=0):
    query = """
        SELECT c.id, c.materia_id, c.nombre, c.anio, c.cuatrimestre
        FROM cursos c
        WHERE c.materia_id = %s
    """
    params = [materia_id]
    return paginacion.ejecutar(query, params, "id ASC", page_size, offset)

def contar_cursos_de_materia(materia_id):
    query = """
        SELECT COUNT(*) as total
        FROM cursos
        WHERE materia_id = %s
    """
    result = db.execute_query(query, (materia_id,), un_solo_valor=True)
    return result["total"] if result else 0