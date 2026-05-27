from flask import request, jsonify, Blueprint
import services.evaluaciones_service as logic
from config import ADMIN, DOCENTE, AYUDANTE
from utils.error_handlers import (
    created_response,
    ValidationError
)
from utils import auth_validator as auth

evaluaciones_bp = Blueprint("evaluaciones", __name__)

@evaluaciones_bp.get("/health")
def health_check():
    return jsonify({"resource": "evaluaciones", "status": "ok"})

@evaluaciones_bp.route("/", methods=["GET"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def obtener_evaluaciones():

    curso_id = request.args.get("curso_id")
    tipo_evaluacion_id = request.args.get("tipo_evaluacion_id")
    titulo = request.args.get("titulo")
    fecha = request.args.get("fecha")
    activo = request.args.get("activo")

    evaluaciones, total = logic.obtener_evaluaciones(
        curso_id,
        tipo_evaluacion_id,
        titulo,
        fecha,
        activo
    )

    if not evaluaciones:
        return "", 204

    return jsonify({
        "evaluaciones": evaluaciones,
        "total": total
    }), 200


@evaluaciones_bp.route("/", methods=["POST"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def crear_evaluacion():

    parametros = request.get_json()
    nueva_evaluacion = logic.crear_evaluacion(parametros)

    return created_response(
        {
            "message": "Evaluación creada exitosamente",
            "evaluacion": nueva_evaluacion
        },
        f"/evaluaciones/{nueva_evaluacion['id']}"
    )


@evaluaciones_bp.route("/<int:id>", methods=["GET"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def obtener_evaluacion_por_id(id):
    evaluacion = logic.obtener_evaluacion_por_id(id)
    return jsonify(evaluacion), 200


@evaluaciones_bp.route("/<int:id>", methods=["PUT"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def reemplazar_evaluacion(id):
    parametros = request.get_json()
    actualizado = logic.reemplazar_evaluacion(id, parametros)
    if not actualizado:
        return {"error": "Evaluación no encontrada"}, 404

    return "", 204


@evaluaciones_bp.route("/<int:id>", methods=["DELETE"])
@auth.requiere_roles(ADMIN, DOCENTE)
def eliminar_evaluacion(id):
    logic.eliminar_evaluacion(id)
    return "", 204


@evaluaciones_bp.route("/<id>", methods=["GET", "PUT", "DELETE"])
def evaluacion_id_invalido(id):
    raise ValidationError(
        "El ID debe ser un número entero positivo."
    )