import email
from uuid import uuid4

import mysql.connector

import repositories.estudiante_curso_repository as db
import repositories.estudiantes_repository as estudiantes_repo
import repositories.cursos_repository as cursos_repo
from utils.csv_handler import leer_csv
from utils.error_handlers import NotFoundError, DuplicateError, ValidationError
import clients.email_client as EmailClient


def _validar_estudiante_y_curso(estudiante_id, curso_id):
    if not estudiantes_repo.obtener_estudiante_por_id(estudiante_id):
        raise NotFoundError("No se encontró el estudiante para la inscripción.")
    if not cursos_repo.obtener_curso_por_id(curso_id):
        raise NotFoundError("No se encontró el curso para la inscripción.")


def _validar_inscripciones_abiertas(curso_id):
    """Bloquea inscribir alumnos nuevos si el curso no está 'abierta'.
    Solo aplica al alta de inscripciones, no a editar inscripciones existentes."""
    curso = cursos_repo.obtener_curso_por_id(curso_id)
    if curso and curso.get("estado") and curso["estado"] != "abierta":
        raise ValidationError("Las inscripciones de este curso están cerradas.")


def obtener_estudiante_cursos(estudiante_id=None, curso_id=None, estado=None, q=None,
                              page_size=20, offset=0):
    return db.obtener_estudiante_cursos(
        estudiante_id, curso_id, estado, q,
        page_size=page_size, offset=offset
    )


def crear_estudiante_curso(parametros):
    estudiante_id = parametros["estudiante_id"]
    curso_id = parametros["curso_id"]
    estado = parametros["estado"]

    _validar_estudiante_y_curso(estudiante_id, curso_id)
    _validar_inscripciones_abiertas(curso_id)

    if db.existe_inscripcion(estudiante_id, curso_id):
        raise DuplicateError("El estudiante ya está inscripto en este curso.")

    try:
        estudiante_curso = db.crear_estudiante_curso(estudiante_id, curso_id, estado)
        print(f"Inscripción creada con ID {estudiante_curso['id']} para estudiante_id {estudiante_id} en curso_id {curso_id}", flush=True)

        estudiante = estudiantes_repo.obtener_estudiante_por_id(estudiante_id)
        curso = cursos_repo.obtener_curso_por_id(curso_id)
        token = estudiante["token_qr"]  # QR único por estudiante (no por inscripción)

        print(f"Enviando email de bienvenida al estudiante {estudiante['nombre']} {estudiante['apellido']} ({estudiante['email']}) para el curso {curso['nombre']} con token {token}", flush=True)
        EmailClient.enviar_email_bienvenida_qr(
            to=estudiante["email"],
            nombre_alumno=estudiante["nombre"],
            apellido_alumno=estudiante["apellido"],
            curso_nombre=curso["nombre"],
            token=token,
        )

        print(f"Email de bienvenida enviado al estudiante {estudiante['nombre']} {estudiante['apellido']} ({estudiante['email']}) para el curso {curso['nombre']}", flush=True)
        return estudiante_curso

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
    filas = leer_csv(archivo_file, columnas_requeridas={'padron', 'curso_id'})

    guardados = 0
    ignorados_duplicados = 0
    errores = []
    cursos_cache = {}  # evita reconsultar el mismo curso por cada fila

    for index, fila in enumerate(filas):
        nro_linea = index + 2  # +1 por el encabezado, +1 porque enumerate arranca en 0

        try:
            padron = int(str(fila['padron']).strip())
            curso_id = int(str(fila['curso_id']).strip())
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

        if curso_id not in cursos_cache:
            cursos_cache[curso_id] = cursos_repo.obtener_curso_por_id(curso_id)
        curso = cursos_cache[curso_id]
        if not curso:
            errores.append({
                "linea": nro_linea,
                "error": f"No se encontró un curso con id {curso_id}"
            })
            continue
        if curso.get("estado") and curso["estado"] != "abierta":
            errores.append({
                "linea": nro_linea,
                "error": f"Las inscripciones del curso {curso_id} están cerradas."
            })
            continue

        if db.existe_inscripcion(estudiante_id, curso_id):
            ignorados_duplicados += 1
            continue

        try:
            crear_estudiante_curso({
                "estudiante_id": estudiante_id,
                "curso_id": curso_id,
                "estado": "activo",
            })
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
