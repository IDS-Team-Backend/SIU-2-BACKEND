from . import materiales_repository as db
from modules.cursos import cursos_repository
from modules.usuarios import usuarios_repository
from utils.error_handlers import ValidationError, NotFoundError


def obtener_materiales(curso_id=None, subido_por=None, page_size=20, offset=0):
    registros, total = db.obtener_todos(curso_id, subido_por, page_size, offset)
    return registros, total


def obtener_material_por_id(id):
    material = db.obtener_por_id(id)
    if not material:
        raise NotFoundError(f"No existe un material con el ID {id}")
    return material


def crear_material(data):
    curso_id    = data.get("curso_id")
    titulo      = data.get("titulo", "").strip() if data.get("titulo") else None
    archivo_url = data.get("archivo_url", "").strip() if data.get("archivo_url") else None
    subido_por  = data.get("subido_por")

    # Validación de presencia
    if not curso_id:
        raise ValidationError("curso_id es requerido")
    if not titulo:
        raise ValidationError("titulo es requerido")
    if not archivo_url:
        raise ValidationError("archivo_url es requerida")

    # Validación de longitud
    if len(titulo) > 255:
        raise ValidationError("titulo no puede superar 255 caracteres")
    if len(archivo_url) > 255:
        raise ValidationError("archivo_url no puede superar 255 caracteres")

    # Validación de existencia de entidades padre
    if not cursos_repository.obtener_curso_por_id(curso_id):
        raise NotFoundError(f"No existe un curso con el ID {curso_id}")

    if subido_por and not usuarios_repository.obtener_usuario_por_id(subido_por):
        raise NotFoundError(f"No existe un usuario con el ID {subido_por}")

    return db.insertar(curso_id, titulo, archivo_url, subido_por)


def reemplazar_material(id, data):
    if not db.obtener_por_id(id):
        raise NotFoundError(f"No existe un material con el ID {id}")

    required = ["curso_id", "titulo", "archivo_url"]
    for field in required:
        if not data.get(field):
            raise ValidationError(f"El campo '{field}' es obligatorio")

    curso_id    = data["curso_id"]
    titulo      = data["titulo"].strip()
    archivo_url = data["archivo_url"].strip()
    subido_por  = data.get("subido_por")

    if len(titulo) > 255:
        raise ValidationError("titulo no puede superar 255 caracteres")
    if len(archivo_url) > 255:
        raise ValidationError("archivo_url no puede superar 255 caracteres")

    if not cursos_repository.obtener_curso_por_id(curso_id):
        raise NotFoundError(f"No existe un curso con el ID {curso_id}")

    if subido_por and not usuarios_repository.obtener_usuario_por_id(subido_por):
        raise NotFoundError(f"No existe un usuario con el ID {subido_por}")

    db.actualizar(id, curso_id, titulo, archivo_url, subido_por)


def actualizar_material(id, data):
    if not db.obtener_por_id(id):
        raise NotFoundError(f"No existe un material con el ID {id}")

    if not data:
        raise ValidationError("No se enviaron campos para actualizar")

    if "titulo" in data:
        if not data["titulo"] or not data["titulo"].strip():
            raise ValidationError("titulo no puede estar vacío")
        if len(data["titulo"]) > 255:
            raise ValidationError("titulo no puede superar 255 caracteres")

    if "archivo_url" in data:
        if not data["archivo_url"] or not data["archivo_url"].strip():
            raise ValidationError("archivo_url no puede estar vacía")
        if len(data["archivo_url"]) > 255:
            raise ValidationError("archivo_url no puede superar 255 caracteres")

    if "curso_id" in data:
        if not cursos_repository.obtener_curso_por_id(data["curso_id"]):
            raise NotFoundError(f"No existe un curso con el ID {data['curso_id']}")

    if "subido_por" in data and data["subido_por"]:
        if not usuarios_repository.obtener_usuario_por_id(data["subido_por"]):
            raise NotFoundError(f"No existe un usuario con el ID {data['subido_por']}")

    db.actualizar_parcial(id, data)


def eliminar_material(id, hard_delete=False):
    if not db.obtener_por_id(id):
        raise NotFoundError(f"No existe un material con el ID {id}")
    db.eliminar(id, hard=hard_delete)