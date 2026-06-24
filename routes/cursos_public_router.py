from flask import jsonify, Blueprint

import services.cursos_service as logic
from utils.error_handlers import ValidationError

# Lectura pública (sin token) del curso enriquecido para la home pública /curso.
# Devuelve la misma info que ya se muestra públicamente (materia, equipo docente
# sin datos sensibles, y stats).
cursos_public_bp = Blueprint("cursos_public", __name__)


@cursos_public_bp.route("/activa", methods=["GET"])
def obtener_curso_activo():
    curso = logic.obtener_curso_activo()
    return jsonify(curso), 200


@cursos_public_bp.route("/<int:curso_id>", methods=["GET"])
def obtener_curso_publico(curso_id):
    curso = logic.obtener_curso_publico(curso_id)
    return jsonify(curso), 200


@cursos_public_bp.get("/<int:curso_id>/cronograma")
def obtener_cronograma_publico(curso_id):
    semanas = logic.get_cronograma(curso_id)
    return jsonify({"semanas": semanas}), 200


@cursos_public_bp.route("/<curso_id>", methods=["GET"])
def curso_publico_id_invalido(curso_id):
    raise ValidationError("El ID de curso debe ser un número entero positivo.")
