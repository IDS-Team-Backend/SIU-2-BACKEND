import repositories.clases_repository as db
import repositories.profesores_repository as profesores_db
from services import cursos_service
from config import ADMIN, ESTADOS_CLASE
from utils.error_handlers import NotFoundError, ValidationError
import utils.validators as validator
import utils.auth_validator as auth

CLASE_PARAMS_OBLIGATORIOS = ["nombre", "profesor_id", "curso_id", "fecha_hora_inicio", "fecha_hora_fin"]
CLASE_PARAMS_OPCIONALES = ["tema", "status"]
CLASE_FILTROS_PERMITIDOS = ["status", "profesor_id", "curso_id", "fecha", "activa"]


def validar_profesor_asignado(profesor_id):
    profesor = profesores_db.obtener_profesor_por_id(profesor_id)
    if not profesor:
        raise NotFoundError("Profesor no existe")
    if not profesor["activo"]:
        raise ValidationError("El profesor asignado está dado de baja.")


def validar_permisos_para_crear_clase(profesor_id):
    if auth.usuario_es(ADMIN):
        return
    perfil = profesores_db.obtener_profesor_por_usuario_id(auth.obtener_usuario_id())
    if not perfil or perfil["id"] != profesor_id:
        raise ValidationError("Los docentes solo pueden asignarse a sí mismos como profesor de una clase.")
    
def validar_disponibilidad_profesor(profesor_id, fecha_hora_inicio, fecha_hora_fin, clase_id=None):
    """Comprueba si el profesor está libre en el rango horario indicado."""
    clase_superpuesta = db.buscar_clase_superpuesta(
            profesor_id, 
            fecha_hora_inicio, 
            fecha_hora_fin, 
            clase_id
        )
    
    if clase_superpuesta:
        raise ValidationError(f"El profesor tiene una clase superpuesta: {clase_superpuesta['nombre']} (ID: {clase_superpuesta['id']}) que va desde {clase_superpuesta['fecha_hora_inicio']} hasta {clase_superpuesta['fecha_hora_fin']}.")

def validar_clase(parametros, parametros_obligatorios, estado_default=ESTADOS_CLASE[0], clase_por_actualizarse=None):
    # limpiar los espacios de los argumentos
    for key, value in parametros.items():
            if isinstance(value, str):
                parametros[key] = value.strip()

    # validar que esten todos los campos obligatorios
    for campo in parametros_obligatorios:
        if (campo not in parametros) or (not parametros[campo]):
            raise ValidationError(f"El campo '{campo}' es obligatorio.")
        
    # validar que no vengan campos que no existen o estan prohibidos (como deleted_at o id )
    for campo in (parametros.keys()):
        if campo not in CLASE_PARAMS_OBLIGATORIOS + CLASE_PARAMS_OPCIONALES:
            raise ValidationError(f"El campo '{campo}' no es válido para una clase.")
      
    nombre = parametros["nombre"]
    profesor_id = parametros["profesor_id"]
    curso_id = parametros["curso_id"]
    fecha_hora_inicio = parametros["fecha_hora_inicio"]
    fecha_hora_fin = parametros["fecha_hora_fin"]
    tema = parametros.get("tema")
    status = parametros.get("status", estado_default)

    validator.validar_fecha_hora(fecha_hora_inicio)
    validator.validar_fecha_hora(fecha_hora_fin)
    validator.validar_rango_fecha(fecha_hora_inicio, fecha_hora_fin)

    cursos_service.obtener_curso(curso_id)

    validar_permisos_para_crear_clase(profesor_id)

    validar_profesor_asignado(profesor_id)
    
    if status != ESTADOS_CLASE[1]:
        # que no tenga ninguna clase superpuesta en ese rango horario
        validar_disponibilidad_profesor(parametros["profesor_id"], parametros["fecha_hora_inicio"], parametros["fecha_hora_fin"], clase_por_actualizarse)

    if not validator.es_estado_clase_valido(status):
        raise ValidationError(f"Estado de clase inválido. Estados válidos: {', '.join(ESTADOS_CLASE)}")

# ─── GET /clases ───────────────────────────────────────────────────────────────
def get_clases(filtros):
    # valida que los filtros enviados son correctos 
    for filtro in filtros.keys():
        if filtro not in CLASE_FILTROS_PERMITIDOS:
            raise ValidationError(f"Filtro '{filtro}' no permitido. Filtros permitidos: {', '.join(CLASE_FILTROS_PERMITIDOS)}")
        
    # parseo de 'true' o 'false' a booleanos de python
    if 'activa' in filtros:
        if filtros['activa'].lower() == 'true':
            filtros['activa'] = True
        elif filtros['activa'].lower() == 'false':
            filtros['activa'] = False
            if not auth.usuario_es(ADMIN):
                raise ValidationError("El filtro 'activa=false' solo puede ser utilizado por administradores.")
        else:
            raise ValidationError("El filtro 'activa' debe ser un valor booleano (true o false).")

    if 'status' in filtros and not validator.es_estado_clase_valido(filtros['status']):
        raise ValidationError(f"Estado de clase inválido en filtro. Estados válidos: {', '.join(ESTADOS_CLASE)}")

    if 'fecha' in filtros:
        validator.validar_fecha(filtros['fecha'])

    clases, total = db.get_clases(filtros)
    
    return clases, total

# ─── GET /clases/{id} ──────────────────────────────────────────────────────────
def get_clase_by_id(clase_id):
    clase = db.get_clase_by_id(clase_id)

    if auth.usuario_es(ADMIN):
        # los admin pueden ver las clases eliminadas
        clase = db.get_clase_by_id(clase_id, incluir_eliminadas=True)

    if not clase:
        raise NotFoundError("Clase no encontrada")

    return clase

# ─── POST /clases ──────────────────────────────────────────────────────────────
def crear_clase(parametros):
    validar_clase(parametros, CLASE_PARAMS_OBLIGATORIOS)

    new_clase = db.crear_clase(parametros["nombre"], parametros["profesor_id"], parametros["curso_id"], parametros["fecha_hora_inicio"], parametros["fecha_hora_fin"], parametros.get("tema"), parametros.get("status", ESTADOS_CLASE[0]))

    return new_clase

# ─── PUT /clases/{id} ──────────────────────────────────────────────────────────────
def actualizar_clase(clase_id, parametros):
    clase_por_actualizarse = get_clase_by_id(clase_id)

    if clase_por_actualizarse["deleted_at"] is not None:
        raise ValidationError("No se puede modificar una clase eliminada.")

    if not auth.usuario_es(ADMIN) and auth.obtener_usuario_id() != clase_por_actualizarse["profesor_id"]:
        raise ValidationError("Los docentes solo pueden modificar sus propias clases.")
    
    if clase_por_actualizarse["status"] == "finalizada" and not auth.usuario_es(ADMIN):
        raise ValidationError("No se pueden modificar ni eliminar clases que ya finalizaron.")
    
    validar_clase(parametros, CLASE_PARAMS_OBLIGATORIOS, estado_default=clase_por_actualizarse["status"], clase_por_actualizarse=clase_id)
    
    clase_actualizada = db.actualizar_clase(
        clase_id,
        parametros["nombre"],
        parametros["profesor_id"],
        parametros["curso_id"],
        parametros["fecha_hora_inicio"],
        parametros["fecha_hora_fin"],
        parametros.get("tema", clase_por_actualizarse["tema"]),
        parametros.get("status", clase_por_actualizarse["status"]),
    )

    return clase_actualizada


# ─── PATCH /clases/{id} ──────────────────────────────────────────────────────────────
def actualizar_clase_parcial(clase_id, parametros):
    # le sacamos los espacios al diccionario original
    for key, value in parametros.items():
        if isinstance(value, str):
            parametros[key] = value.strip()

    clase_por_actualizarse = get_clase_by_id(clase_id)

    if not auth.usuario_es(ADMIN) and auth.obtener_usuario_id() != clase_por_actualizarse["profesor_id"]:
        raise ValidationError("Los docentes solo pueden modificar sus propias clases.")
    
    if clase_por_actualizarse["deleted_at"] is not None:
        raise ValidationError("No se puede modificar una clase eliminada.")
    
    if clase_por_actualizarse["status"] == "finalizada" and not auth.usuario_es(ADMIN):
        raise ValidationError("No se pueden modificar ni eliminar clases que ya finalizaron.")
    
    # validar que no vengan campos que no existen o estan prohibidos (como deleted_at o id )
    for campo in (parametros.keys()):
        if campo not in CLASE_PARAMS_OBLIGATORIOS + CLASE_PARAMS_OPCIONALES:
            raise ValidationError(f"El campo '{campo}' no es válido para una clase.")

    # me devuelve como se veria la clase final, asi la puedo validar
    clase_actualizada_temporalmente = {
        "nombre": parametros.get("nombre", clase_por_actualizarse["nombre"]),
        "profesor_id": parametros.get("profesor_id", clase_por_actualizarse["profesor_id"]),
        "curso_id": parametros.get("curso_id", clase_por_actualizarse["curso_id"]),
        "fecha_hora_inicio": parametros.get("fecha_hora_inicio", str(clase_por_actualizarse["fecha_hora_inicio"])),
        "fecha_hora_fin": parametros.get("fecha_hora_fin", str(clase_por_actualizarse["fecha_hora_fin"])),
        "tema": parametros.get("tema", clase_por_actualizarse["tema"]),
        "status": parametros.get("status", clase_por_actualizarse["status"])
    }



    # En PATCH validamos solo el payload final combinado, no campos obligatorios.
    validar_clase(clase_actualizada_temporalmente, [], clase_por_actualizarse=clase_id)

    clase_actualizada = db.actualizar_clase_parcial(clase_id, parametros)

    return clase_actualizada
 
# ─── DELETE /clases/{id} ──────────────────────────────────────────────────────────────
def eliminar_clase(clase_id):
    clase_por_eliminarse = get_clase_by_id(clase_id)

    if not clase_por_eliminarse:
        raise NotFoundError("Clase no encontrada")
    
    if clase_por_eliminarse["deleted_at"] is not None:
        raise ValidationError("La clase ya ha sido eliminada.")
    
    if clase_por_eliminarse["status"] == "finalizada" and not auth.usuario_es(ADMIN):
        raise ValidationError("No se pueden modificar ni eliminar clases que ya finalizaron.")

    if not auth.usuario_es(ADMIN) and auth.obtener_usuario_id() != clase_por_eliminarse["profesor_id"]:
        raise ValidationError("Los docentes solo pueden eliminar sus propias clases.")
    
    db.eliminar_clase(clase_id)

    return