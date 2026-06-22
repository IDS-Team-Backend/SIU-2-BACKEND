from config import ADMIN
from . import cursos_repository as db
from modules.profesores import profesores_repository as profesores_db
from modules.curso_docentes import curso_docentes_repository as curso_docentes_db
from constants import ALUMNO, DOCENTE, ESTADOS_CURSO
from modules.clases import clases_service as clases_service
from utils.error_handlers import NotFoundError, ValidationError, DuplicateError, ForbiddenError
import mysql.connector
from modules.estudiantes import estudiantes_repository as estudiantes_db
from utils import auth_validator as auth
from modules.estudiante_curso import estudiante_curso_repository as curso_estudiantes_db

curso_params = ["materia_id", "nombre", "anio", "cuatrimestre"]
curso_update_params = ["materia_id", "nombre", "anio", "cuatrimestre"]

def obtener_cursos_del_usuario_actual(usuario_id, rol):
    if rol == ALUMNO:
        estudiante = estudiantes_db.obtener_estudiante_por_usuario_id(usuario_id)
        cursos = db.obtener_cursos_del_alumno(estudiante["id"])
    elif rol == DOCENTE:
        profesor = profesores_db.obtener_profesor_por_usuario_id(usuario_id)
        if not profesor:
            raise NotFoundError("El usuario no tiene un perfil docente activo.")
        cursos = db.obtener_cursos_del_docente(profesor["id"])
    elif rol == ADMIN:
        cursos = db.obtener_todos_los_cursos()
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

def get_cronograma(curso_id):
    return clases_service.get_cronograma(curso_id)


def obtener_curso_activo():
    curso_id = db.obtener_curso_activo_id() or db.obtener_primer_curso_id()
    if not curso_id:
        raise NotFoundError("No hay cursadas cargadas.")
    return obtener_curso_publico(curso_id)


def activar_curso(curso_id):
    curso = db.obtener_curso_por_id(curso_id)
    if not curso:
        raise NotFoundError("No se encontró el curso")

    # Una cursada finalizada (anterior) está congelada: no se reactiva.
    # Para avanzar la cátedra se crea la siguiente cursada.
    if curso["estado"] == "finalizada":
        raise ValidationError(
            "No se puede activar una cursada finalizada (es una cursada anterior)."
        )

    # Al activar otra cursada, la que estaba activa se finaliza (decisión de negocio).
    activo_actual = db.obtener_curso_activo_id()
    if activo_actual and activo_actual != curso_id:
        db.finalizar_curso(activo_actual)

    return db.activar_curso(curso_id)


def crear_siguiente_cursada():
    """Avanza la cátedra: crea una cursada nueva (misma materia, próximo cuatrimestre),
    copia el equipo docente de la actual, la deja activa y finaliza la anterior."""
    actual_id = db.obtener_curso_activo_id()
    if not actual_id:
        raise NotFoundError("No hay una cursada activa para tomar como base.")
    actual = db.obtener_curso_detalle(actual_id)

    # Solo se crea la siguiente cuando la actual ya está finalizada (cerrada).
    if actual["estado"] != "finalizada":
        raise ValidationError(
            "Primero finalizá la cursada actual (cerrar cursada) antes de crear la siguiente."
        )

    # Próximo cuatrimestre: 1 -> 2 (mismo año), 2 -> 1 (año siguiente).
    if actual["cuatrimestre"] == 1:
        anio, cuatrimestre = actual["anio"], 2
    else:
        anio, cuatrimestre = actual["anio"] + 1, 1

    if db.existe_cursada_en_periodo(actual["materia_id"], anio, cuatrimestre):
        raise DuplicateError(
            f"Ya existe una cursada para {anio} · {cuatrimestre}º cuatrimestre."
        )

    nueva = db.crear_cursada(
        materia_id=actual["materia_id"],
        nombre=f"{anio} · {cuatrimestre}º cuatrimestre",
        anio=anio,
        cuatrimestre=cuatrimestre,
        descripcion=actual.get("descripcion"),
        modalidad=actual.get("modalidad"),
        carrera=actual.get("carrera"),
        horas_semanales=actual.get("horas_semanales"),
    )

    # Copiar el equipo docente de la cursada actual a la nueva.
    for d in curso_docentes_db.obtener_por_curso(actual_id):
        curso_docentes_db.agregar(nueva["id"], d["docente_id"], d["rol"])

    # Activar la nueva (finaliza la actual).
    return activar_curso(nueva["id"])


def cambiar_estado(curso_id, nuevo_estado):
    if nuevo_estado not in ESTADOS_CURSO:
        raise ValidationError(
            f"Estado de cursada inválido. Estados válidos: {', '.join(ESTADOS_CURSO)}."
        )

    curso = db.obtener_curso_por_id(curso_id)
    if not curso:
        raise NotFoundError("No se encontró el curso")

    actual = curso["estado"]
    delta = ESTADOS_CURSO.index(nuevo_estado) - ESTADOS_CURSO.index(actual)
    if abs(delta) != 1:
        raise ValidationError(
            "Transición de estado no permitida: solo se puede avanzar o retroceder un paso."
        )

    # Reabrir (retroceder) solo se permite en la cursada activa: una cursada
    # anterior (ya superada por una posterior) queda congelada.
    if delta < 0 and not curso["activa"]:
        raise ValidationError(
            "No se puede reabrir una cursada anterior: ya se activó una cursada posterior."
        )

    return db.cambiar_estado(curso_id, nuevo_estado)

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

def validar_usuario_tiene_acceso_a_curso(curso_id):
    if auth.usuario_es(ALUMNO):
        estudiante = estudiantes_db.obtener_estudiante_por_usuario_id(auth.obtener_usuario_id())
        if not estudiante:
            raise NotFoundError("El usuario no tiene un perfil estudiante asociado.")
        if not curso_estudiantes_db.obtener_estudiante_curso_por_estudiante_curso(estudiante["id"], curso_id):
            raise ForbiddenError("No formas parte del curso.")
        return
    
    if auth.usuario_es(DOCENTE):
        profesor = profesores_db.obtener_profesor_por_usuario_id(auth.obtener_usuario_id())
        if not profesor:
            raise NotFoundError("El usuario no tiene un perfil docente activo.")
        if not curso_docentes_db.docente_pertenece_activamente_a_curso(profesor["id"], curso_id):
            raise ForbiddenError("No formas parte del curso.")
        return

def obtener_curso(id):
    curso = db.obtener_curso_detalle(id)
    if not curso:
        raise NotFoundError("No se encontró el curso")
    
    validar_usuario_tiene_acceso_a_curso(id)

    return curso


def obtener_curso_publico(id):
    """Curso enriquecido (materia + equipo docente + stats), apto para mostrar
    sin autenticación. El equipo docente va SIN email/legajo (display-safe)."""
    curso = db.obtener_curso_detalle(id)
    if not curso:
        raise NotFoundError("No se encontró el curso")

    docentes = db.obtener_docentes_por_cursos([id]) or []
    curso["equipo_docente"] = [
        {
            "docente_id": d["docente_id"],
            "nombre": d["nombre"],
            "apellido": d["apellido"],
            "rol": d["rol"],
        }
        for d in docentes
    ]
    curso["stats"] = db.obtener_stats(id)
    return curso

def eliminar_curso(id: int, hard_delete=False):
    curso = db.obtener_curso_por_id(id, hard_delete)
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
    validar_campos_descriptivos(parametros)

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

def validar_campos_descriptivos(parametros):
    """Valida los campos opcionales que se editan desde la gestión de la cursada."""
    descripcion = parametros.get("descripcion")
    modalidad = parametros.get("modalidad")
    carrera = parametros.get("carrera")
    horas = parametros.get("horas_semanales")

    if descripcion is not None and not isinstance(descripcion, str):
        raise ValidationError("El campo 'descripcion' debe ser texto.")

    if modalidad is not None and (not isinstance(modalidad, str) or len(modalidad) > 50):
        raise ValidationError("El campo 'modalidad' debe ser texto de hasta 50 caracteres.")

    if carrera is not None and (not isinstance(carrera, str) or len(carrera) > 150):
        raise ValidationError("El campo 'carrera' debe ser texto de hasta 150 caracteres.")

    if horas is not None and (not isinstance(horas, int) or isinstance(horas, bool) or horas < 0):
        raise ValidationError("El campo 'horas_semanales' debe ser un entero mayor o igual a 0.")


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