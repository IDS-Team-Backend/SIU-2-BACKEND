import repositories.clases_repository as db 
from services import cursos_service
import services.usuarios_service as usuarios_service
from config import ROLES, ESTADOS_CLASE
from utils.error_handlers import NotFoundError, ValidationError
import utils.validators as validator

clase_params_obligatorios = ["nombre", "profesor_id", "curso_id", "fecha_hora"]
clase_params_opcionales = ["tema", "status"]

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
    for campo in clase_params_obligatorios:
        if (campo not in parametros) or (not parametros[campo]):
            raise ValidationError(f"El campo '{campo}' es obligatorio.")

    nombre = parametros["nombre"]
    profesor_id = parametros["profesor_id"]
    curso_id = parametros["curso_id"]
    fecha_hora = parametros["fecha_hora"]
    tema = parametros.get("tema")
    status = parametros.get("status", ESTADOS_CLASE[0]) # caso default 

    validator.validar_fecha_hora(fecha_hora)

    profesor = usuarios_service.obtener_usuario_por_id(profesor_id)
    if not profesor:
        raise NotFoundError("Profesor no existe")
    if profesor['rol_id'] != ROLES.get("docente"):
        raise ValidationError("El usuario asignado como profesor no tiene el rol adecuado.")
    
    cursos_service.obtener_curso(curso_id)

    if not validator.es_estado_clase_valido(status):
        raise ValidationError(f"Estado de clase inválido. Estados válidos: {', '.join(ESTADOS_CLASE)}")

    new_clase = db.crear_clase(nombre, profesor_id, curso_id, fecha_hora, tema, status)

    return new_clase