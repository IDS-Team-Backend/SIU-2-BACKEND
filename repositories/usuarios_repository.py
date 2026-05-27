from config import ADMIN, ALUMNO, DOCENTE
import db
from werkzeug.security import generate_password_hash


def obtener_usuarios(
    nombre=None,
    apellido=None,
    email=None,
    dni=None,
    rol=None,
):

    query = "FROM usuarios u WHERE 1=1"
    params = []
    if nombre:
        query += " AND u.nombre LIKE %s"
        params.append(f"%{nombre}%")

    if apellido:
        query += " AND u.apellido LIKE %s"
        params.append(f"%{apellido}%")

    if email:
        query += " AND u.email LIKE %s"
        params.append(f"%{email}%")

    if dni:
        query += " AND u.dni = %s"
        params.append(dni)



    if rol == ADMIN:
        query += " AND u.es_admin = TRUE"

    if rol == ALUMNO:
        query += " AND EXISTS (SELECT 1 FROM estudiantes e WHERE e.usuario_id = u.id AND e.activo = TRUE)"

    if rol == DOCENTE:
        query += " AND EXISTS (SELECT 1 FROM profesores p WHERE p.usuario_id = u.id AND p.activo = TRUE)"

    if rol == "pendiente": # usuarios sin perfil asignado, solo para admins
        query += """ 
                    AND u.es_admin = FALSE 
                    AND NOT EXISTS (SELECT 1 FROM estudiantes e WHERE e.usuario_id = u.id AND e.activo = TRUE)
                    AND NOT EXISTS (SELECT 1 FROM profesores p WHERE p.usuario_id = u.id AND p.activo = TRUE)
                """

    count_query = "SELECT COUNT(*) as total " + query
    count_usuarios = db.execute_query(
        count_query,
        tuple(params),
        un_solo_valor=True
    )
    total = count_usuarios["total"] if count_usuarios else 0
    select_query = """
        SELECT
            u.id,
            u.nombre,
            u.apellido,
            u.email,
            u.dni,
            u.es_admin,
            u.activo,
            u.created_at
    """ + query + " ORDER BY u.id ASC"

    lista_usuarios = db.execute_query(
        select_query,
        tuple(params)
    )

    return lista_usuarios, total


def crear_usuario(nombre, apellido, email, dni, password, es_admin=False):

    password_hash = generate_password_hash(password)

    query = """
        INSERT INTO usuarios
        (nombre, apellido, email, dni, password_hash, es_admin)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    params = (
        nombre,
        apellido,
        email,
        dni,
        password_hash,
        es_admin,
    )

    new_id = db.execute_query(query, params, modifica_db=True)

    return obtener_usuario_por_id(new_id)


def obtener_usuario_por_id(id):
    query = """
        SELECT
        u.id,
        u.nombre,
        u.apellido,
        u.email,
        u.dni,
        u.es_admin,
        u.activo
    FROM usuarios u
    WHERE u.id = %s
    """
    resultado = db.execute_query(query, (id,), un_solo_valor=True)
    return resultado


def eliminar_usuario(id: int):
    query = "UPDATE usuarios SET activo = FALSE WHERE id = %s"
    filas_afectadas = db.execute_query(query, (id,), modifica_db=True)
    return filas_afectadas > 0


def existe_email(email, excluir_id=None):
    if excluir_id is not None:
        query = "SELECT COUNT(*) as total FROM usuarios WHERE email = %s AND id != %s"
        result = db.execute_query(query, (email, excluir_id), un_solo_valor=True)
    else:
        query = "SELECT COUNT(*) as total FROM usuarios WHERE email = %s"
        result = db.execute_query(query, (email,), un_solo_valor=True)
    return result['total'] > 0 if result else False


def existe_dni(dni, excluir_id=None):
    if excluir_id is not None:
        query = "SELECT COUNT(*) as total FROM usuarios WHERE dni = %s AND id != %s"
        result = db.execute_query(query, (dni, excluir_id), un_solo_valor=True)
    else:
        query = "SELECT COUNT(*) as total FROM usuarios WHERE dni = %s"
        result = db.execute_query(query, (dni,), un_solo_valor=True)
    return result['total'] > 0 if result else False


def reemplazar_usuario(id, nombre, apellido, email, dni, es_admin, activo):
    query = """
        UPDATE usuarios
        SET
            nombre = %s,
            apellido = %s,
            email = %s,
            dni = %s,
            es_admin = %s,
            activo = %s
        WHERE id = %s
    """
    params = (
        nombre,
        apellido,
        email,
        dni,
        es_admin,
        activo,
        id,
    )
    filas = db.execute_query(
        query,
        params,
        modifica_db=True
    )

    return filas > 0


def get_user_by_dni(dni):
    query = "SELECT * FROM usuarios WHERE dni = %s"
    params = (dni,)

    result = db.execute_query(query, params)

    return result[0] if result else None


def get_user_by_email(email):
    query = "SELECT * FROM usuarios WHERE email = %s"
    params = (email,)

    result = db.execute_query(query, params)

    return result[0] if result else None
