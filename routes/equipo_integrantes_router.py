from flask import request, jsonify, Blueprint
import services.equipo_integrantes_service as logic
from utils.error_handlers import (
    created_response,
    ValidationError
)
from utils import auth_validator as auth

equipo_integrantes_bp = Blueprint(
    "equipo_integrantes",
    __name__
)

equipo_integrantes_bp.before_request(
    auth.validar_token
)

@equipo_integrantes_bp.route("/", methods=["GET"])
@auth.requiere_roles("profesor", "ayudante")
def obtener_integrantes():
    equipo_id = request.args.get("equipo_id")
    alumno_id = request.args.get("alumno_id")
    integrantes, total = logic.obtener_integrantes(
        equipo_id,
        alumno_id
    )
    if not integrantes:
        return "", 204
    return jsonify({
        "integrantes": integrantes,
        "total": total
    }), 200

@equipo_integrantes_bp.route("/", methods=["POST"])
@auth.requiere_roles("profesor", "ayudante")
def agregar_integrante():
    parametros = request.get_json()
    integrante = logic.agregar_integrante(parametros)
    return created_response(
        {
            "message": "Integrante agregado exitosamente",
            "integrante": integrante
        },
        "/equipo-integrantes/"
    )

@equipo_integrantes_bp.route(
    "/<int:equipo_id>/<int:alumno_id>",
    methods=["DELETE"]
)
@auth.requiere_roles("profesor", "ayudante")
def eliminar_integrante(equipo_id,alumno_id):
    logic.eliminar_integrante(equipo_id,alumno_id)
    return "", 204

@equipo_integrantes_bp.route("/<equipo_id>/<alumno_id>",methods=["DELETE"])
def integrante_id_invalido(equipo_id,alumno_id):
    raise ValidationError(
        "Los IDs deben ser números enteros positivos."
    )