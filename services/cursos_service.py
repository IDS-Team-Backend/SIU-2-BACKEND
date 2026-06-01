import repositories.cursos_repository as db
import repositories.profesores_repository as profesores_db
from config import ALUMNO, DOCENTE
from utils.error_handlers import NotFoundError, ValidationError, DuplicateError, ForbiddenError
import mysql.connector

curso_params = ["materia_id", "nombre", "anio", "cuatrimestre"]
curso_update_params = ["materia_id", "nombre", "anio", "cuatrimestre"]

def obtener_cursos_del_usuario_actual(usuario_id, rol):
    if rol == ALUMNO:
        cursos = db.obtener_cursos_del_alumno(usuario_id)
    elif rol == DOCENTE:
        profesor = profesores_db.obtener_profesor_por_usuario_id(usuario_id)
        if not profesor or not profesor.get("activo"):
            raise NotFoundError("El usuario no tiene un perfil docente activo.")
        cursos = db.obtener_cursos_del_docente(profesor["id"])
    else:
        raise ForbiddenError("No tenés permisos para acceder a este recurso.")

    return cursos

def obtener_cursos(materia_id=None, nombre=None, anio=None, cuatrimestre=None, profesor_id=None, page_size=20, offset=0):
    cursos, total = db.obtener_cursos(materia_id, nombre, anio, cuatrimestre, profesor_id, page_size, offset)

    if not cursos: 
        return [], 0
    
    # se guarda el id de todos los cursos obtenidos en una lista 
    curso_ids = [curso["id"] for curso in cursos]

    print("estos son los curso_ids: ", curso_ids, flush=True)
    # se consigue el equipo docente de cada curso en una query
    docentes_por_curso = db.obtener_docentes_por_cursos(curso_ids)

    print("estos son los docentes_por_curso: ", docentes_por_curso, flush=True)

    # se le asigna el docente respectivo a cada curso
    for curso in cursos:
        curso["equipo_docente"] = [
            {
                "docente_id": docente["docente_id"],
                "nombre": docente["nombre"],
                "apellido": docente["apellido"],
                "rol": docente["rol"]
            }
            for docente in docentes_por_curso if docente["curso_id"] == curso["id"]
        ]

    return cursos, total

def crear_cursos(parametros):
    if not parametros or not isinstance(parametros, dict):
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    for campo in curso_params:
        if (campo not in parametros) or (parametros[campo] is None):
            raise ValidationError(f"El campo '{campo}' es requerido.")

    materia_id = parametros["materia_id"]
    nombre = parametros["nombre"]
    anio = parametros["anio"]
    cuatrimestre = parametros["cuatrimestre"]

    validar_datos_curso(materia_id, nombre, anio, cuatrimestre)

    if not db.existe_materia(materia_id):
        raise NotFoundError("No se encontró la materia asociada al curso.")

    if db.existe_curso(materia_id, nombre, anio, cuatrimestre):
        raise DuplicateError("Ya existe un curso con esos datos.")

    try:
        return db.crear_cursos(materia_id, nombre, anio, cuatrimestre)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe un curso con esos datos.")

def obtener_curso(id):
    curso = db.obtener_curso_por_id(id)
    if not curso:
        raise NotFoundError("No se encontró el curso")
    return curso

def eliminar_curso(id: int):
    curso = db.obtener_curso_por_id(id)
    if not curso:
        raise NotFoundError("No se encontró el curso")
    db.eliminar_curso(id)
    return

def reemplazar_curso(id, parametros):
    if not parametros or not isinstance(parametros, dict):
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    for campo in curso_update_params:
        if (campo not in parametros) or (parametros[campo] is None):
            raise ValidationError(f"El campo '{campo}' es requerido.")

    materia_id = parametros["materia_id"]
    nombre = parametros["nombre"]
    anio = parametros["anio"]
    cuatrimestre = parametros["cuatrimestre"]

    validar_datos_curso(materia_id, nombre, anio, cuatrimestre)

    if not db.obtener_curso_por_id(id):
        raise NotFoundError("No se encontró el curso")

    if not db.existe_materia(materia_id):
        raise NotFoundError("No se encontró la materia asociada al curso.")

    if db.existe_curso(materia_id, nombre, anio, cuatrimestre, excluir_id=id):
        raise DuplicateError("Ya existe otro curso con esos datos.")

    try:
        return db.reemplazar_curso(id, parametros)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("Ya existe otro curso con esos datos.")

def validar_datos_curso(materia_id, nombre, anio, cuatrimestre):
    if not isinstance(materia_id, int) or materia_id <= 0:
        raise ValidationError("El campo 'materia_id' debe ser un entero positivo.")

    if not isinstance(nombre, str) or not nombre.strip():
        raise ValidationError("El campo 'nombre' es requerido.")

    if len(nombre.strip()) > 100:
        raise ValidationError("El campo 'nombre' no puede superar los 100 caracteres.")

    if not isinstance(anio, int) or anio < 2000:
        raise ValidationError("El campo 'anio' debe ser un entero válido mayor o igual a 2000.")

    if not isinstance(cuatrimestre, int) or cuatrimestre not in [1, 2]:
        raise ValidationError("El campo 'cuatrimestre' debe ser 1 o 2.")