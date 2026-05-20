import db
from werkzeug.security import generate_password_hash


def obtener_usuarios(
    nombre=None,
    apellido=None,
    email=None,
    dni=None,
    rol_id=None
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

    if rol_id:
        query += " AND u.rol_id = %s"
        params.append(rol_id)

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
            u.rol_id,
            u.activo,
            u.created_at
    """ + query + " ORDER BY u.id ASC"

    lista_usuarios = db.execute_query(
        select_query,
        tuple(params)
    )

    return lista_usuarios, total


def crear_usuario(nombre, apellido, email, dni, password, rol_id):

    password_hash = generate_password_hash(password)

    query = """
        INSERT INTO usuarios
        (nombre, apellido, email, dni, password_hash, rol_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    params = (
        nombre,
        apellido,
        email,
        dni,
        password_hash,
        rol_id
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
        u.rol_id,
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


def reemplazar_usuario(id,nombre,apellido,email,dni,rol_id,activo):
    query = """
        UPDATE usuarios
        SET
            nombre = %s,
            apellido = %s,
            email = %s,
            dni = %s,
            rol_id = %s,
            activo = %s
        WHERE id = %s
    """
    params = (
        nombre,
        apellido,
        email,
        dni,
        rol_id,
        activo,
        id
    )
    filas = db.execute_query(
        query,
        params,
        modifica_db=True
    )

    return filas > 0

def get_user_types(): 
    query = "SELECT id, nombre FROM tipos_usuario"

    result = db.execute_query(query)

    return result

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