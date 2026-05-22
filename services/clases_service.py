import repositories.clases_repository as db 
from utils.error_handlers import NotFoundError, ValidationError
import utils.service_validator as validator

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