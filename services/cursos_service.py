import repositories.cursos_repository as db
from utils.error_handlers import NotFoundError, ValidationError, DuplicateError
import mysql.connector


global curso_params
curso_params = ["materia_id", "nombre", "anio", "cuatrimestre"]

curso_update_params = ["materia_id", "nombre", "anio", "cuatrimestre"]


def obtener_cursos(materia_id=None, nombre=None, anio=None, cuatrimestre=None):
    return db.obtener_cursos(materia_id, nombre, anio, cuatrimestre)


def crear_cursos(parametros):
    for campo in curso_params:
        if (campo not in parametros) or (parametros[campo] is None):
            raise ValidationError(f"El campo '{campo}' es requerido.")

    materia_id = parametros["materia_id"]
    nombre = parametros["nombre"]
    anio = parametros["anio"]
    cuatrimestre = parametros["cuatrimestre"]

    validar_datos_curso(parametros["materia_id"], parametros["nombre"], parametros["anio"], parametros["cuatrimestre"])

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


def remplazar_curso(id, parametros):
    for campo in curso_update_params:
        if (campo not in parametros) or (parametros[campo] is None):
            raise ValidationError(f"El campo '{campo}' es requerido.")

    materia_id = parametros["materia_id"]
    nombre = parametros["nombre"]
    anio = parametros["anio"]
    cuatrimestre = parametros["cuatrimestre"]

    validar_datos_curso(materia_id, nombre, anio, cuatrimestre)

    if not db.existe_materia(materia_id):
        raise NotFoundError("No se encontró la materia asociada al curso.")

    if db.existe_curso(materia_id, nombre, anio, cuatrimestre, excluir_id=id):
        raise DuplicateError("Ya existe otro curso con esos datos.")

    try:
        return db.remplazar_curso(
            id,parametros
        )
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