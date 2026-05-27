import repositories.clases_repository as db
import repositories.profesores_repository as profesores_db
import validators.clases_validator as clases_validator
from services import cursos_service
from config import ADMIN, ESTADOS_CLASE
from utils.error_handlers import NotFoundError, ValidationError
import utils.auth_validator as auth


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
        clase_id,
    )
    if clase_superpuesta:
        raise ValidationError(
            f"El profesor tiene una clase superpuesta: {clase_superpuesta['nombre']} "
            f"(ID: {clase_superpuesta['id']}) que va desde {clase_superpuesta['fecha_hora_inicio']} "
            f"hasta {clase_superpuesta['fecha_hora_fin']}."
        )


def _validar_negocio_clase(parametros, clase_por_actualizarse=None):
    profesor_id = parametros["profesor_id"]
    fecha_hora_inicio = parametros["fecha_hora_inicio"]
    fecha_hora_fin = parametros["fecha_hora_fin"]
    status = parametros.get("status", ESTADOS_CLASE[0])

    cursos_service.obtener_curso(parametros["curso_id"])
    validar_permisos_para_crear_clase(profesor_id)
    validar_profesor_asignado(profesor_id)

    if status != ESTADOS_CLASE[1]:
        validar_disponibilidad_profesor(
            profesor_id, fecha_hora_inicio, fecha_hora_fin, clase_por_actualizarse
        )


# ─── GET /clases ───────────────────────────────────────────────────────────────
def get_clases(filtros):
    filtros = clases_validator.validar_filtros_clases(filtros, auth.usuario_es(ADMIN))
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
    parametros = clases_validator.validar_body_crear_clase(parametros)
    _validar_negocio_clase(parametros)

    new_clase = db.crear_clase(
        parametros["nombre"],
        parametros["profesor_id"],
        parametros["curso_id"],
        parametros["fecha_hora_inicio"],
        parametros["fecha_hora_fin"],
        parametros.get("tema"),
        parametros.get("status", ESTADOS_CLASE[0]),
    )
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

    parametros = clases_validator.validar_body_reemplazar_clase(parametros)
    _validar_negocio_clase(parametros, clase_por_actualizarse=clase_id)

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
    parametros = clases_validator.validar_body_modificar_clase_parcial(parametros)

    clase_por_actualizarse = get_clase_by_id(clase_id)

    if not auth.usuario_es(ADMIN) and auth.obtener_usuario_id() != clase_por_actualizarse["profesor_id"]:
        raise ValidationError("Los docentes solo pueden modificar sus propias clases.")

    if clase_por_actualizarse["deleted_at"] is not None:
        raise ValidationError("No se puede modificar una clase eliminada.")

    if clase_por_actualizarse["status"] == "finalizada" and not auth.usuario_es(ADMIN):
        raise ValidationError("No se pueden modificar ni eliminar clases que ya finalizaron.")

    # Construir cómo queda la clase tras el merge y revalidar consistencia + disponibilidad.
    clase_merged = {
        "nombre": parametros.get("nombre", clase_por_actualizarse["nombre"]),
        "profesor_id": parametros.get("profesor_id", clase_por_actualizarse["profesor_id"]),
        "curso_id": parametros.get("curso_id", clase_por_actualizarse["curso_id"]),
        "fecha_hora_inicio": parametros.get("fecha_hora_inicio", str(clase_por_actualizarse["fecha_hora_inicio"])),
        "fecha_hora_fin": parametros.get("fecha_hora_fin", str(clase_por_actualizarse["fecha_hora_fin"])),
        "tema": parametros.get("tema", clase_por_actualizarse["tema"]),
        "status": parametros.get("status", clase_por_actualizarse["status"]),
    }
    clase_merged = clases_validator.validar_body_reemplazar_clase(clase_merged)
    _validar_negocio_clase(clase_merged, clase_por_actualizarse=clase_id)

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
