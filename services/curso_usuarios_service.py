import pandas as pd
from utils.error_handlers import ValidationError, NotFoundError
import repositories.curso_usuarios_repository as db
from repositories import usuarios_repository, cursos_repository
from repositories import estudiantes_repository as estudiantes_repo
from utils.error_handlers import ValidationError

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
    if not db.obtener_por_id(id):
        raise NotFoundError(f"No se pudo eliminar: la inscripción con ID {id} no existe.")

    db.eliminar(id)


def importar_inscripciones_por_lote(archivo_file):
    if not archivo_file:
        raise ValidationError("No se proporcionó ningún archivo")

    try:
        df = pd.read_csv(archivo_file)
    except Exception as e:
        raise ValidationError(f"Error al leer el archivo CSV: {str(e)}")

    columnas_requeridas = {'padron', 'curso_id'}
    if not columnas_requeridas.issubset(df.columns):
        raise ValidationError("El archivo debe contener las columnas 'padron' y 'curso_id'")

    guardados = 0
    ignorados_duplicados = 0
    errores = []

    for index, fila in df.iterrows():
        nro_linea = index + 2
        
        try:
            padron = int(fila['padron'])
            curso_id = int(fila['curso_id'])
        except (ValueError, TypeError):
            errores.append({
                "linea": nro_linea,
                "error": "El padrón o el curso_id contienen valores numéricos inválidos o vacíos."
            })
            continue

       # Si existe
        estudiante = estudiantes_repo.obtener_estudiante_por_padron(padron)
        if not estudiante:
            errores.append({
                "linea": nro_linea,
                "error": f"No se encontró un estudiante con el padrón {padron}"
            })
            continue

        usuario_id = estudiante['usuario_id']

        # Si esta ya esta iscrito lo ignora
        if db.existe_inscripcion(usuario_id, curso_id):
            ignorados_duplicados += 1
            continue

        try:
            db.insertar(usuario_id, curso_id, "activo")
            guardados += 1
        except Exception as e:
            errores.append({
                "linea": nro_linea,
                "error": f"Error inesperado en la base de datos: {str(e)}"
            })

    return {
        "procesados_exito": guardados,
        "ignorados_duplicados": ignorados_duplicados,
        "errores_encontrados": len(errores),
        "detalles_errores": errores
    }