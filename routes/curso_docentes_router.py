from flask import request, jsonify, Blueprint

import services.curso_docentes_service as logic
from constants import ADMIN, DOCENTE, ROLES_STAFF
from utils.error_handlers import created_response, ValidationError
from utils import auth_validator as auth
from validators import curso_docentes_validator


curso_docentes_bp = Blueprint("curso_docentes", __name__)


@curso_docentes_bp.route("/", methods=["GET"])
@auth.requiere_roles(*ROLES_STAFF)
def obtener_equipo_docente():
    curso_id = request.args.get("curso_id", type=int)
    if not curso_id:
        raise ValidationError("El parámetro 'curso_id' es obligatorio.")

    integrantes = logic.obtener_equipo_docente(curso_id)

    if not integrantes:
        return "", 204

    return jsonify({"integrantes": integrantes, "total": len(integrantes)}), 200


@curso_docentes_bp.route("/participaciones", methods=["GET"])
@auth.requiere_roles(*ROLES_STAFF)
def obtener_participaciones():
    """Participaciones de varios docentes: ?docente_ids=1,2,3 (una sola query)."""
    raw = request.args.get("docente_ids", "")
    ids = [int(x) for x in raw.split(",") if x.strip().isdigit()]
    if not ids:
        return "", 204

    participaciones = logic.obtener_participaciones_por_docentes(ids)
    if not participaciones:
        return "", 204

    return jsonify({"participaciones": participaciones, "total": len(participaciones)}), 200


@curso_docentes_bp.route("/", methods=["POST"])
@auth.requiere_roles(*ROLES_STAFF)
def agregar_integrante():
    parametros = curso_docentes_validator.validar_body_agregar_integrante(request.get_json())
    integrante = logic.agregar_integrante(
        parametros["curso_id"], parametros["docente_id"], parametros["rol"]
    )
    return created_response(
        {"message": "Integrante agregado al curso", "integrante": integrante},
        f"/curso_docentes/{integrante['id']}"
    )


@curso_docentes_bp.route("/<int:id>", methods=["PATCH"])
@auth.requiere_roles(*ROLES_STAFF)
def cambiar_participacion(id):
    parametros = curso_docentes_validator.validar_body_cambiar_participacion(request.get_json())
    integrante = logic.cambiar_participacion(id, parametros["rol"])
    return jsonify({
        "message": "Tipo de participación actualizado",
        "integrante": integrante,
    }), 200


@curso_docentes_bp.route("/<int:id>", methods=["DELETE"])
@auth.requiere_roles(*ROLES_STAFF)
def quitar_integrante(id):
    logic.quitar_integrante(id)
    return "", 204


@curso_docentes_bp.route("/<id>", methods=["GET", "PATCH", "DELETE"])
def integrante_id_invalido(id):
    raise ValidationError("El ID debe ser un número entero positivo.")
