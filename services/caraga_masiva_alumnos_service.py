import repositories.estudiante_curso_repository as db
import repositories.estudiantes_repository as estudiantes_repo
import repositories.cursos_repository as cursos_repo
from utils.error_handlers import ValidationError, NotFoundError, DuplicateError
import mysql.connector


 
def inscribir_lote_por_ids(curso_id, estudiante_ids, estado="activo"):
    #valida el curso que estan
    curso = cursos_repo.obtener_curso_por_id(curso_id)

    if not curso:     
        raise NotFoundError(f"No se encontró un curso con id {curso_id}")
    if curso.get("estado") and curso["estado"] != "abierta":
        raise ValidationError(f"Las inscripciones del curso {curso_id} están cerradas.")
 
    if not isinstance(estudiante_ids, list) or not estudiante_ids:
        raise ValidationError("Se requiere una lista no vacía de estudiante_ids.")
    
    guardados = 0
    duplicados = 0
    errores = []

    for est_id in estudiante_ids:
        # valida tipo
        try:
            est_id = int(est_id)
        except (ValueError, TypeError):
            errores.append({"estudiante_id": est_id, "error": "id inválido"})
            continue
        # valida que exsista
        if not estudiantes_repo.obtener_estudiante_por_id(est_id):
            errores.append({"estudiante_id": est_id, "error": "estudiante inexistente"})
            continue
        #duplicados
        if db.existe_inscripcion(est_id, curso_id):
            duplicados += 1
            continue

        try:
            db.crear_estudiante_curso(est_id, curso_id, estado)
            guardados += 1
        except mysql.connector.errors.IntegrityError:
            duplicados += 1
        except Exception as e:
            errores.append({"estudiante_id": est_id, "error": str(e)})


    return {
        "procesados_exito": guardados,
        "ignorados_duplicados": duplicados,
        "errores_encontrados": len(errores),
        "detalles_errores": errores,
    }


