import repositories.notas_repository as db
import repositories.evaluaciones_repository as evaluaciones_db
import repositories.estudiantes_repository as estudiantes_db
import repositories.equipos_repository as equipos_db
from utils.error_handlers import (
    ValidationError,
    NotFoundError,
    DuplicateError
)
from utils.validaciones import (
    validar_body_presente,
    validar_entero
)

nota_params = [
    "evaluacion_id",
    "nota"
]
nota_update_params = [
    "nota"
]

def obtener_notas(evaluacion_id=None,alumno_id=None,equipo_id=None):
    return db.obtener_notas(
        evaluacion_id,
        alumno_id,
        equipo_id
    )

def crear_nota(parametros):
    validar_body_presente(parametros)
    for campo in nota_params:
        if campo not in parametros:
            raise ValidationError(
                f"El campo '{campo}' es requerido."
            )
            
    evaluacion_id = validar_entero(
        parametros["evaluacion_id"],
        "evaluacion_id"
    )
    nota = parametros["nota"]
    observaciones = parametros.get("observaciones") 
    
    evaluacion = evaluaciones_db.obtener_evaluacion_por_id(evaluacion_id)
    if not evaluacion:
        raise NotFoundError("No se encontró la evaluación")
        
    alumno_id = parametros.get("alumno_id")
    equipo_id = parametros.get("equipo_id")
    
    if evaluacion["es_grupal"]:
        if not equipo_id:
            raise ValidationError("Las evaluaciones grupales requieren equipo_id.")
        equipo = equipos_db.obtener_equipo_por_id(equipo_id)
        if not equipo:
            raise NotFoundError("No se encontró el equipo")
        if db.existe_nota_equipo(evaluacion_id, equipo_id):
            raise DuplicateError("El equipo ya tiene una nota cargada.")
        
        return db.crear_nota_grupal(
            evaluacion_id,
            equipo_id,
            nota,
            observaciones
        )
    else:
        if not alumno_id:
            raise ValidationError("Las evaluaciones individuales requieren alumno_id.")
        alumno = estudiantes_db.obtener_estudiante_por_id(alumno_id)
        if not alumno:
            raise NotFoundError("No se encontró el alumno")
        if db.existe_nota_alumno(evaluacion_id, alumno_id):
            raise DuplicateError("El alumno ya tiene una nota cargada.")
        
        return db.crear_nota_individual(
            evaluacion_id,
            alumno_id,
            nota,
            observaciones
        )

def obtener_nota_por_id(id):
    nota = db.obtener_nota_por_id(id)
    if not nota:
        raise NotFoundError(
            "No se encontró la nota"
        )
    return nota

def reemplazar_nota(id, parametros):
    validar_body_presente(parametros)
    if "nota" not in parametros:
        raise ValidationError(
            "El campo 'nota' es requerido."
        )
    actualizado = db.reemplazar_nota(
        id,
        parametros["nota"]
    )
    if not actualizado:
        raise NotFoundError(
            "No se encontró la nota"
        )

    return actualizado

def eliminar_nota(id):
    eliminado = db.eliminar_nota(id)
    if not eliminado:
        raise NotFoundError(
            "No se encontró la nota"
        )

    return