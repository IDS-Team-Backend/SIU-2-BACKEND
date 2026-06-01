import mysql.connector
import pandas as pd

import repositories.estudiante_curso_repository as db
import repositories.estudiantes_repository as estudiantes_repo
import repositories.cursos_repository as cursos_repo
from utils.error_handlers import NotFoundError, DuplicateError, ValidationError


def _validar_estudiante_y_curso(estudiante_id, curso_id):
    if not estudiantes_repo.obtener_estudiante_por_id(estudiante_id):
        raise NotFoundError("No se encontró el estudiante para la inscripción.")
    if not cursos_repo.obtener_curso_por_id(curso_id):
        raise NotFoundError("No se encontró el curso para la inscripción.")


def obtener_estudiante_cursos(estudiante_id=None, curso_id=None, estado=None,
                              page_size=20, offset=0):
    return db.obtener_estudiante_cursos(
        estudiante_id, curso_id, estado,
        page_size=page_size, offset=offset
    )


def crear_estudiante_curso(parametros):
    estudiante_id = parametros["estudiante_id"]
    curso_id = parametros["curso_id"]
    estado = parametros["estado"]

    _validar_estudiante_y_curso(estudiante_id, curso_id)

    if db.existe_inscripcion(estudiante_id, curso_id):
        raise DuplicateError("El estudiante ya está inscripto en este curso.")

    try:
        return db.crear_estudiante_curso(estudiante_id, curso_id, estado)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("El estudiante ya está inscripto en este curso.")


def obtener_estudiante_curso_por_id(id):
    estudiante_curso = db.obtener_estudiante_curso_por_id(id)

    if not estudiante_curso:
        raise NotFoundError("No se encontró la inscripción.")

    return estudiante_curso


def reemplazar_estudiante_curso(id, parametros):
    estudiante_id = parametros["estudiante_id"]
    curso_id = parametros["curso_id"]
    estado = parametros["estado"]

    _validar_estudiante_y_curso(estudiante_id, curso_id)

    if db.existe_inscripcion(estudiante_id, curso_id, excluir_id=id):
        raise DuplicateError("El estudiante ya está inscripto en este curso.")

    try:
        return db.reemplazar_estudiante_curso(id, estudiante_id, curso_id, estado)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("El estudiante ya está inscripto en este curso.")


def modificar_estudiante_curso_parcial(id, parametros):
    inscripcion = db.obtener_estudiante_curso_por_id(id)
    if not inscripcion:
        raise NotFoundError("No se encontró la inscripción.")

    estudiante_id = parametros.get("estudiante_id", inscripcion["estudiante_id"])
    curso_id = parametros.get("curso_id", inscripcion["curso_id"])

    if "estudiante_id" in parametros and not estudiantes_repo.obtener_estudiante_por_id(estudiante_id):
        raise NotFoundError("No se encontró el estudiante para la inscripción.")
    if "curso_id" in parametros and not cursos_repo.obtener_curso_por_id(curso_id):
        raise NotFoundError("No se encontró el curso para la inscripción.")

    if ("estudiante_id" in parametros or "curso_id" in parametros) and \
            db.existe_inscripcion(estudiante_id, curso_id, excluir_id=id):
        raise DuplicateError("El estudiante ya está inscripto en este curso.")

    try:
        actualizado = db.modificar_estudiante_curso_parcial(id, parametros)
    except mysql.connector.errors.IntegrityError:
        raise DuplicateError("El estudiante ya está inscripto en este curso.")

    if actualizado is None:
        raise NotFoundError("No se encontró la inscripción.")

    return actualizado


def eliminar_estudiante_curso(id):
    if not db.eliminar_estudiante_curso(id):
        raise NotFoundError("No se encontró la inscripción.")

    return


def importar_inscripciones_por_lote(archivo_file):
    if not archivo_file:
        raise ValidationError("No se proporcionó ningún archivo")

    try:
        df = pd.read_csv(archivo_file)
    except Exception as e:
        raise ValidationError(f"Error al leer el archivo CSV: {str(e)}")

    columnas_requeridas = {'padron', 'curso_id'}
    if not columnas_requeridas.issubset(df.columns):
        raise ValidationError("El archivo debe contener las columnas 'padron' y 'curso_id'")

    guardados = 0
    ignorados_duplicados = 0
    errores = []

    for index, fila in df.iterrows():
        nro_linea = index + 2

        try:
            padron = int(fila['padron'])
            curso_id = int(fila['curso_id'])
        except (ValueError, TypeError):
            errores.append({
                "linea": nro_linea,
                "error": "El padrón o el curso_id contienen valores numéricos inválidos o vacíos."
            })
            continue

        estudiante = estudiantes_repo.obtener_estudiante_por_padron(padron)
        if not estudiante:
            errores.append({
                "linea": nro_linea,
                "error": f"No se encontró un estudiante con el padrón {padron}"
            })
            continue

        estudiante_id = estudiante['id']

        if db.existe_inscripcion(estudiante_id, curso_id):
            ignorados_duplicados += 1
            continue

        try:
            db.crear_estudiante_curso(estudiante_id, curso_id, "activo")
            guardados += 1
        except Exception as e:
            errores.append({
                "linea": nro_linea,
                "error": f"Error inesperado en la base de datos: {str(e)}"
            })

    return {
        "procesados_exito": guardados,
        "ignorados_duplicados": ignorados_duplicados,
        "errores_encontrados": len(errores),
        "detalles_errores": errores
    }
