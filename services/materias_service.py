import repositories.materias_repository as db
from utils.error_handlers import NotFoundError, ValidationError, DuplicateError
import mysql.connector

materia_params = ["nombre"]
materia_update_params = ["nombre", "codigo"]

def obtener_materias(nombre=None, codigo=None, page_size=20, offset=0):
    return db.obtener_materias(nombre, codigo, page_size, offset)

def crear_materias(parametros):
    if not parametros or not isinstance(parametros, dict):
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    for campo in materia_params:
        if (campo not in parametros) or (parametros[campo] is None):
            raise ValidationError(f"El campo '{campo}' es requerido.")

    nombre = parametros["nombre"]
    codigo = parametros.get("codigo")

    validar_datos_materia(nombre, codigo)

    if codigo and db.existe_codigo(codigo):
        raise DuplicateError("Ya existe una materia con ese código.")

    try:
        return db.crear_materia(nombre, codigo)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe una materia con ese código.")

def obtener_materia_por_id(materia_id):
    materia = db.obtener_materia_por_id(materia_id)
    if not materia:
        raise NotFoundError("No se encontró la materia")
    return materia

def reemplazar_materia(materia_id, parametros):
    if not parametros or not isinstance(parametros, dict):
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    for campo in materia_update_params:
        if campo not in parametros:
            raise ValidationError(f"El campo '{campo}' es requerido.")

    nombre = parametros["nombre"]
    codigo = parametros.get("codigo")

    validar_datos_materia(nombre, codigo)

    if not db.obtener_materia_por_id(materia_id):
        raise NotFoundError("No se encontró la materia")

    if codigo and db.existe_codigo(codigo, excluir_id=materia_id):
        raise DuplicateError("Ya existe otra materia con ese código.")

    try:
        return db.reemplazar_materia(materia_id, parametros)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe otra materia con ese código.")

def eliminar_materia(materia_id: int):
    materia = db.obtener_materia_por_id(materia_id)
    if not materia:
        raise NotFoundError("No se encontró la materia")

    total_cursos = db.contar_cursos_de_materia(materia_id)

    if total_cursos > 0:
        raise ValidationError("No se puede eliminar la materia porque tiene cursos asociados.")

    db.eliminar_materia(materia_id)
    return

def obtener_cursos_de_materia(materia_id, page_size=20, offset=0):
    materia = db.obtener_materia_por_id(materia_id)
    if not materia:
        raise NotFoundError("No se encontró la materia")
    return db.obtener_cursos_de_materia(materia_id, page_size, offset)

def validar_datos_materia(nombre, codigo=None):
    if not isinstance(nombre, str) or not nombre.strip():
        raise ValidationError("El campo 'nombre' es requerido.")

    if len(nombre.strip()) > 150:
        raise ValidationError("El campo 'nombre' no puede superar los 150 caracteres.")

    if codigo is not None:
        if not isinstance(codigo, str):
            raise ValidationError("El campo 'codigo' debe ser texto.")

        if codigo.strip() == "":
            raise ValidationError("El campo 'codigo' no puede estar vacío. Usá null si no tiene código.")

        if len(codigo.strip()) > 50:
            raise ValidationError("El campo 'codigo' no puede superar los 50 caracteres.")