from flask import request, jsonify, Blueprint
import services.equipos_service as logic
from config import ADMIN, ALUMNO, AYUDANTE, DOCENTE
from utils.error_handlers import (
    created_response,
    ValidationError
)
from utils import auth_validator as auth

equipos_bp = Blueprint("equipos", __name__)

@equipos_bp.get("/health")
def health_check():
    return jsonify({"resource": "equipos", "status": "ok"})

@equipos_bp.route("/", methods=["GET"])
@auth.requiere_roles("DOCENTE", "AYUDANTE")
def obtener_equipos():

    curso_id = request.args.get("curso_id")
    evaluacion_id = request.args.get("evaluacion_id")
    nombre = request.args.get("nombre")
    activo = request.args.get("activo")

    equipos, total = logic.obtener_equipos(
        curso_id,
        evaluacion_id,
        nombre,
        activo
    )

    if not equipos:
        return "", 204

    return jsonify({
        "equipos": equipos,
        "total": total
    }), 200


@equipos_bp.route("/", methods=["POST"])
@auth.requiere_roles("DOCENTE", "AYUDANTE")
def crear_equipo():
    parametros = request.get_json()
    nuevo_equipo = logic.crear_equipo(parametros)

    return created_response(
        {
            "message": "Equipo creado exitosamente",
            "equipo": nuevo_equipo
        },
        f"/equipos/{nuevo_equipo['id']}"
    )


@equipos_bp.route("/<int:id>", methods=["GET"])
@auth.requiere_roles("DOCENTE", "AYUDANTE")
def obtener_equipo_por_id(id):
    equipo = logic.obtener_equipo_por_id(id)
    return jsonify(equipo), 200


@equipos_bp.route("/<int:id>", methods=["PUT"])
@auth.requiere_roles("DOCENTE", "AYUDANTE")
def reemplazar_equipo(id):
    parametros = request.get_json()
    actualizado = logic.reemplazar_equipo(id, parametros)

    if not actualizado:
        return {"error": "Equipo no encontrado"}, 404

    return "", 204


@equipos_bp.route("/<int:id>", methods=["DELETE"])
@auth.requiere_roles("DOCENTE")
def eliminar_equipo(id):
    logic.eliminar_equipo(id)
    return "", 204


@equipos_bp.route("/<int:id>", methods=["GET", "PUT", "DELETE"])
def equipo_id_invalido(id):
    raise ValidationError(
        "El ID debe ser un número entero positivo."
    )