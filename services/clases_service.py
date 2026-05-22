import repositories.clases_repository as db 
from services import cursos_service
import services.usuarios_service as usuarios_service
from config import ADMIN, DOCENTE, ROLES, ESTADOS_CLASE
from utils.error_handlers import NotFoundError, ValidationError
import utils.validators as validator
import utils.auth_validator as auth

clase_params_obligatorios = ["nombre", "profesor_id", "curso_id", "fecha_hora"]
clase_params_opcionales = ["tema", "status"]

def validar_clase(parametros, parametros_obligatorios, estado_default=ESTADOS_CLASE[0]):
    for campo in parametros_obligatorios:
        if (campo not in parametros) or (not parametros[campo]):
            raise ValidationError(f"El campo '{campo}' es obligatorio.")
        
    nombre = parametros["nombre"]
    profesor_id = parametros["profesor_id"]
    curso_id = parametros["curso_id"]
    fecha_hora = parametros["fecha_hora"]
    tema = parametros.get("tema")
    status = parametros.get("status", estado_default)

    validator.validar_fecha_hora(fecha_hora)

    if not auth.usuario_es_admin() and not auth.usuario_es_docente():
        raise ValidationError(f"Solo los usuarios con rol {DOCENTE} o {ADMIN} pueden crear o modificar clases.")
    
    if not auth.usuario_es_admin() and auth.obtener_usuario_id() != profesor_id:
        # si el usuario no es admin, entonces el debe ser el profesor asignado a la clase
        raise ValidationError("Los docentes solo pueden asignarse a sí mismos como profesor de una clase.")

    profesor = usuarios_service.obtener_usuario_por_id(profesor_id)
    if not profesor:
        raise NotFoundError("Profesor no existe")
    if profesor['rol_id'] != ROLES.get(DOCENTE):
        raise ValidationError("El usuario asignado como profesor no tiene el rol adecuado.")
    
    cursos_service.obtener_curso(curso_id)

    if not validator.es_estado_clase_valido(status):
        raise ValidationError(f"Estado de clase inválido. Estados válidos: {', '.join(ESTADOS_CLASE)}")

def get_clases(filtros): 
    if 'fecha' in filtros:
        validator.validar_fecha(filtros['fecha'])

    clases, total = db.get_clases(filtros)
    
    return clases, total

def get_clase_by_id(clase_id):
    clase = db.get_clase_by_id(clase_id)

    if not clase:
        raise NotFoundError("Clase no encontrada")

    return clase

def crear_clase(parametros):
    validar_clase(parametros, clase_params_obligatorios)

    new_clase = db.crear_clase(parametros["nombre"], parametros["profesor_id"], parametros["curso_id"], parametros["fecha_hora"], parametros.get("tema"), parametros.get("status", ESTADOS_CLASE[0]))

    return new_clase

def actualizar_clase(clase_id, parametros):
    clase_params = clase_params_obligatorios + clase_params_opcionales
    validar_clase(parametros, clase_params, estado_default="")

    clase_por_actualizarse = get_clase_by_id(clase_id)

    if not clase_por_actualizarse:
        raise NotFoundError("Clase no encontrada")

    if auth.usuario_es_docente() and auth.obtener_usuario_id() != clase_por_actualizarse["profesor_id"]:
        raise ValidationError("Los docentes solo pueden modificar sus propias clases.")
    
    clase_actualizada = db.actualizar_clase(clase_id, parametros["nombre"], parametros["profesor_id"], parametros["curso_id"], parametros["fecha_hora"], parametros.get("tema"), parametros.get("status"))

    return clase_actualizada