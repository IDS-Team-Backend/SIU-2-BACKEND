import db
from utils import paginacion


def obtener_cursos_del_alumno(usuario_id):
    query = """
        SELECT c.id, c.nombre, c.anio, c.cuatrimestre
        FROM curso_usuarios cu
        INNER JOIN cursos c ON c.id = cu.curso_id
        WHERE cu.usuario_id = %s
          AND cu.estado = 'activo'
        ORDER BY c.id ASC
    """
    return db.execute_query(query, (usuario_id,)) or []


def obtener_cursos_del_docente(docente_id):
    query = """
        SELECT c.id, c.nombre, c.anio, c.cuatrimestre
        FROM curso_docentes cd
        INNER JOIN cursos c ON c.id = cd.curso_id
        WHERE cd.docente_id = %s
        ORDER BY c.id ASC
    """
    return db.execute_query(query, (docente_id,)) or []

def obtener_cursos(materia_id=None, nombre=None, anio=None, cuatrimestre=None, docente_id=None, page_size=20, offset=0):
    query = """
        SELECT c.id, c.materia_id, c.nombre, c.anio, c.cuatrimestre
        FROM cursos c
    """
    
    # si se filtra por docente, hay que hacer un join
    if docente_id:
        query += " INNER JOIN curso_docentes cd ON c.id = cd.curso_id"

    query += " WHERE 1=1"
    params = []

    if docente_id:
        query += " AND cd.docente_id = %s"
        params.append(docente_id)

    if materia_id:
        query += " AND c.materia_id = %s"
        params.append(materia_id)

    if nombre:
        query += " AND c.nombre LIKE %s"
        params.append(f"%{nombre}%")

    if anio:
        query += " AND c.anio = %s"
        params.append(anio)

    if cuatrimestre:
        query += " AND c.cuatrimestre = %s"
        params.append(cuatrimestre)

    return paginacion.ejecutar(query, params, "c.id ASC", page_size, offset)

def obtener_docentes_por_cursos(curso_ids):
    if not curso_ids:
        return []
        
    # se necesita un %s por cada curso que haya 
    placeholders = ', '.join(['%s'] * len(curso_ids))
    
    query = f"""
        SELECT 
            cd.curso_id, 
            cd.docente_id, 
            cd.nombre AS rol, 
            u.nombre, 
            u.apellido
        FROM curso_docentes cd
        INNER JOIN profesores p ON cd.docente_id = p.id
        INNER JOIN usuarios u ON p.usuario_id = u.id
        WHERE cd.curso_id IN ({placeholders})
    """
    
    return db.execute_query(query, tuple(curso_ids))

def crear_cursos(materia_id, nombre, anio, cuatrimestre):
    query = """
        INSERT INTO cursos (materia_id, nombre, anio, cuatrimestre)
        VALUES (%s, %s, %s, %s)
    """
    values = (materia_id, nombre.strip(), anio, cuatrimestre)
    nuevo_id = db.execute_query(query, values, modifica_db=True)
    return obtener_curso_por_id(nuevo_id)

def obtener_curso_por_id(curso_id):
    query = "SELECT * FROM cursos WHERE id = %s"
    return db.execute_query(query, (curso_id,), un_solo_valor=True)

def eliminar_curso(curso_id):
    query = "DELETE FROM cursos WHERE id = %s"
    db.execute_query(query, (curso_id,), modifica_db=True)
    return True

def reemplazar_curso(curso_id, params):
    query = """
        UPDATE cursos
        SET materia_id = %s, nombre = %s, anio = %s, cuatrimestre = %s
        WHERE id = %s
    """
    values = (
        params["materia_id"],
        params["nombre"].strip(),
        params["anio"],
        params["cuatrimestre"],
        curso_id
    )
    db.execute_query(query, values, modifica_db=True)
    return obtener_curso_por_id(curso_id)

def existe_materia(materia_id):
    query = "SELECT 1 FROM materias WHERE id = %s"
    result = db.execute_query(query, (materia_id,), un_solo_valor=True)
    return result is not None

def existe_curso(materia_id, nombre, anio, cuatrimestre, excluir_id=None):
    query = """
        SELECT 1 FROM cursos
        WHERE materia_id = %s
          AND nombre = %s
          AND anio = %s
          AND cuatrimestre = %s
    """
    params = [materia_id, nombre.strip(), anio, cuatrimestre]

    if excluir_id is not None:
        query += " AND id != %s"
        params.append(excluir_id)

    result = db.execute_query(query, tuple(params), un_solo_valor=True)
    return result is not None