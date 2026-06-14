import repositories.estudiante_curso_repository as db
import repositories.estudiantes_repository as estudiantes_repo
import repositories.cursos_repository as cursos_repo
from utils.error_handlers import ValidationError, NotFoundError, DuplicateError
import mysql.connector


 
def inscribir_lote_por_ids(curso_id, estudiante_ids, estado="activo"):
    curso = cursos_repo.obtener_cursos_por_id(curso_id)

    if not curso:     
        raise NotFoundError(f"No se encontró un curso con id {curso_id}")
    if curso.get("estado") and curso["estado"] != "abierta":
        raise ValidationError(f"Las inscripciones del curso {curso_id} están cerradas.")
 
    if not isinstance(estudiante_ids, list) or not estudiante_ids:
        raise ValidationError("Se requiere una lista no vacía de estudiante_ids.")

