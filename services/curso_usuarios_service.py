from utils.error_handlers import ValidationError, NotFoundError
import repositories.curso_usuarios_repository as db
from repositories import usuarios_repository, cursos_repository

def obtener_curso_usuarios(usuario_id=None, curso_id=None, estado=None, page_size=20, offset=0):
    
    registros, total = db.obtener_todos(usuario_id, curso_id, estado, page_size, offset)
    return registros, total



def crear_curso_usuario(data):
    usuario_id = data.get("usuario_id")
    curso_id = data.get("curso_id")
    estado = data.get("estado", "activo")

    # Validación: ¿Existen los datos padre en sus respectivas tablas?
    if not usuarios_repository.obtener_usuario_por_id(usuario_id):
        raise NotFoundError(f"No existe un usuario con el ID {usuario_id}")
    
    if not cursos_repository.obtener_curso_por_id(curso_id):
        raise NotFoundError(f"No existe un curso con el ID {curso_id}")

    # Validación de presencia
    if not data.get("usuario_id") or not data.get("curso_id"):
        raise ValidationError("usuario_id y curso_id son requeridos")
    
    # Validación de existencia previa
    if db.existe_inscripcion(data["usuario_id"], data["curso_id"]):
        raise ValidationError("El usuario ya está inscripto en este curso")
    
    # Validación de estado
    estado = data.get("estado", "activo")
    if estado not in ["activo", "suspendido", "baja"]:
        raise ValidationError("Estado inválido")
        
    return db.insertar(data["usuario_id"], data["curso_id"], estado)


def reemplazar_curso_usuario(id, data):
    
    registro_existente = db.obtener_por_id(id)
    if not registro_existente:
        raise NotFoundError(f"No existe el registro con ID {id}")

    # 2. Validar que vengan los datos obligatorios 
    required = ["usuario_id", "curso_id", "estado"]
    for field in required:
        if field not in data:
            raise ValidationError(f"El campo '{field}' es obligatorio")

    # 3. Validar existencia de entidades 
    if not usuarios_repository.obtener_usuario_por_id(data["usuario_id"]):
        raise NotFoundError("Usuario no encontrado")
    if not cursos_repository.obtener_curso_por_id(data["curso_id"]):
        raise NotFoundError("Curso no encontrado")

    # 4. Actualizar
    return db.actualizar(id, data["usuario_id"], data["curso_id"], data["estado"])


def eliminar_curso_usuario(id):
    # 1. Verificamos que exista antes de intentar borrar
    if not db.obtener_por_id(id):
      
        raise NotFoundError(f"No se pudo eliminar: la inscripción con ID {id} no existe.")
    
    
    db.eliminar(id)