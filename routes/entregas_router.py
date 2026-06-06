from flask import request, jsonify, Blueprint
from constants import ADMIN, AYUDANTE, DOCENTE
import services.entregas_service as logic
from utils.error_handlers import (
    created_response,
    ValidationError
)
from utils import auth_validator as auth

entregas_bp = Blueprint("entregas", __name__)

@entregas_bp.route("/", methods=["GET"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def obtener_entregas():
    evaluacion_id = request.args.get("evaluacion_id")
    alumno_id = request.args.get("alumno_id")
    equipo_id = request.args.get("equipo_id")
    entregas, total = logic.obtener_entregas(
        evaluacion_id,
        alumno_id,
        equipo_id
    )
    if not entregas:
        return "", 204

    return jsonify({
        "entregas": entregas,
        "total": total
    }), 200

@entregas_bp.route("/", methods=["POST"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def crear_entrega():
    parametros = request.get_json()
    nueva_entrega = logic.crear_entrega(parametros)
    return created_response(
        {
            "message": "Entrega registrada exitosamente",
            "entrega": nueva_entrega
        },
        f"/entregas/{nueva_entrega['id']}"
    )

@entregas_bp.route("/<int:id>", methods=["GET"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def obtener_entrega_por_id(id):
    entrega = logic.obtener_entrega_por_id(id)
    return jsonify(entrega), 200

@entregas_bp.route("/<int:id>", methods=["PATCH"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def actualizar_entrega(id):
    parametros = request.get_json()
    logic.actualizar_entrega(
        id,
        parametros
    )
    return "", 204

@entregas_bp.route("/<int:id>", methods=["DELETE"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def eliminar_entrega(id):
    logic.eliminar_entrega(id)
    return "", 204

@entregas_bp.route("/<id>", methods=["GET", "PUT", "DELETE"])
def entrega_id_invalido(id):
    raise ValidationError(
        "El ID debe ser un número entero positivo."
    )
