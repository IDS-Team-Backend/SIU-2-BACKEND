import secrets
import string
 
from utils.csv_handler import leer_csv, procesar_lote
from utils.error_handlers import (
    ValidationError, NotFoundError, DuplicateError
)
 
from modules.personas.usuarios import usuarios_repository as usuarios_repo
from . import estudiantes_repository as estudiantes_repo
from modules.cursada.estudiante_curso import estudiante_curso_repository as estudiante_curso_repo
from modules.cursada.estudiante_curso import estudiante_curso_service as estudiante_curso_serv
from modules.cursada.cursos import cursos_repository as cursos_repo
from modules.personas.auth import auth_service as auth_service
 
import mysql.connector
 
 
_COLUMNAS = {"nombre", "apellido", "email", "dni", "padron", "carrera", "anio_ingreso"}
 
 
def _password_inutilizable():
    """64 chars aleatorios — el estudiante no puede loguearse con esto."""
    alfabeto = string.ascii_letters + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(64))
 
 
# Alta masiva de estudiantes desde CSV
def importar_estudiantes_por_lote(archivo_file):
    filas = leer_csv(archivo_file, columnas_requeridas=_COLUMNAS)
 
    def procesar_fila(fila):
        nombre   = (fila.get("nombre")   or "").strip()
        apellido = (fila.get("apellido") or "").strip()
        email    = (fila.get("email")    or "").strip()
        carrera  = (fila.get("carrera")  or "").strip()
 
        # Conversión numérica con mensajes claros
        try:
            dni = int(str(fila.get("dni", "")).strip())
        except (ValueError, TypeError):
            raise ValidationError(f"DNI inválido: '{fila.get('dni')}'")
 
        try:
            padron = int(str(fila.get("padron", "")).strip())
        except (ValueError, TypeError):
            raise ValidationError(f"Padrón inválido: '{fila.get('padron')}'")
 
        try:
            anio_ingreso = int(str(fila.get("anio_ingreso", "")).strip())
        except (ValueError, TypeError):
            raise ValidationError(f"Año de ingreso inválido: '{fila.get('anio_ingreso')}'")
 
        # Validación de datos personales (reutiliza el validador existente)
        auth_service.validar_datos_usuario(nombre, apellido, dni, email, "placeholder")
 
        # Duplicados → se ignoran (no es error fatal)
        if usuarios_repo.get_user_by_dni(dni):
            return "duplicado"
        if usuarios_repo.get_user_by_email(email):
            return "duplicado"
        if estudiantes_repo.obtener_estudiante_por_padron(padron):
            return "duplicado"
 
        # Crear usuario — el repo hashea la contraseña internamente,
        # se le pasa en texto plano (no un hash).
        nuevo_usuario = usuarios_repo.crear_usuario(
            nombre, apellido, email, dni, _password_inutilizable(),
        )
        usuario_id = nuevo_usuario["id"] if isinstance(nuevo_usuario, dict) else nuevo_usuario
 
        # Crear estudiante
        estudiantes_repo.crear_estudiante(usuario_id, padron, carrera, anio_ingreso)
        return "ok"
 
    return procesar_lote(filas, procesar_fila)
 
 
# Inscripción masiva por lista de IDs

def inscribir_lote_por_ids(curso_id, estudiante_ids, estado="activo"):
    curso = cursos_repo.obtener_curso_por_id(curso_id)
    if not curso:
        raise NotFoundError(f"No se encontró un curso con id {curso_id}")
    if curso.get("estado") and curso["estado"] != "abierta":
        raise ValidationError(f"Las inscripciones del curso {curso_id} están cerradas.")
 
    if not isinstance(estudiante_ids, list) or not estudiante_ids:
        raise ValidationError("Se requiere una lista no vacía de estudiante_ids.")
 
    guardados = 0
    duplicados = 0
    errores = []
 
    for est_id in estudiante_ids:
        try:
            est_id = int(est_id)
        except (ValueError, TypeError):
            errores.append({"estudiante_id": est_id, "error": "id inválido"})
            continue
 
        if not estudiantes_repo.obtener_estudiante_por_id(est_id):
            errores.append({"estudiante_id": est_id, "error": "estudiante inexistente"})
            continue
 
        if estudiante_curso_repo.existe_inscripcion(est_id, curso_id):
            duplicados += 1
            continue
 
        try:
            estudiante_curso_serv.crear_estudiante_curso(est_id, curso_id, estado)
            guardados += 1
        except mysql.connector.errors.IntegrityError:
            duplicados += 1
        except Exception as e:
            errores.append({"estudiante_id": est_id, "error": str(e)})
 
    return {
        "procesados_exito": guardados,
        "ignorados_duplicados": duplicados,
        "errores_encontrados": len(errores),
        "detalles_errores": errores,
    }

def desvincular_lote_por_ids(curso_id, estudiante_ids):
    if not isinstance(estudiante_ids, list) or not estudiante_ids:
        raise ValidationError("Se requiere una lista no vacía de estudiante_ids.")

    desvinculados = 0
    errores = []

    for est_id in estudiante_ids:
        try:
            est_id = int(est_id)
        except (ValueError, TypeError):
            errores.append({"estudiante_id": est_id, "error": "id inválido"})
            continue

        # Buscar la inscripción de ese estudiante en ese curso
        inscripcion = estudiante_curso_repo.obtener_por_estudiante_y_curso(est_id, curso_id)
        if not inscripcion:
            errores.append({"estudiante_id": est_id, "error": "no estaba inscripto"})
            continue

        try:
            estudiante_curso_repo.eliminar_estudiante_curso(inscripcion["id"])
            desvinculados += 1
        except Exception as e:
            errores.append({"estudiante_id": est_id, "error": str(e)})

    return {
        "procesados_exito": desvinculados,
        "ignorados_duplicados": 0,
        "errores_encontrados": len(errores),
        "detalles_errores": errores,
    }
