from flask import request, jsonify, Blueprint
from . import equipos_service as logic
from constants import ADMIN, ALUMNO, AYUDANTE, DOCENTE, ROLES_STAFF
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
@auth.requiere_roles(*ROLES_STAFF)
def obtener_equipos():
    curso_id = request.args.get("curso_id")
    evaluacion_id = request.args.get("evaluacion_id")
    nombre = request.args.get("nombre")

    equipos, total = logic.obtener_equipos(
        curso_id,
        evaluacion_id,
        nombre,

    )

    if not equipos:
        return "", 204

    return jsonify({
        "equipos": equipos,
        "total": total
    }), 200


@equipos_bp.route("/", methods=["POST"])
@auth.requiere_roles(*ROLES_STAFF)
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


@equipos_bp.route("/bulk", methods=["POST"])
@auth.requiere_roles(*ROLES_STAFF)
def crear_equipos_bulk():
    if 'archivo' not in request.files:
        return jsonify({"error": "No se encontró la parte del archivo en la petición con la clave 'archivo'"}), 400

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo"}), 400

    resultado_proceso = logic.importar_equipos_por_lote(
        archivo,
        request.form.get("curso_id"),
        request.form.get("evaluacion_id"),
    )
    return jsonify({
        "mensaje": "Procesamiento de lote finalizado",
        "resultado": resultado_proceso
    }), 200


@equipos_bp.route("/<int:id>", methods=["GET"])
@auth.requiere_roles(*ROLES_STAFF)
def obtener_equipo_por_id(id):
    equipo = logic.obtener_equipo_por_id(id)
    return jsonify(equipo), 200


@equipos_bp.route("/<int:id>", methods=["PUT"])
@auth.requiere_roles(*ROLES_STAFF)
def reemplazar_equipo(id):
    parametros = request.get_json()
    actualizado = logic.reemplazar_equipo(id, parametros)

    if not actualizado:
        return {"error": "Equipo no encontrado"}, 404

    return "", 204


@equipos_bp.route("/<int:id>", methods=["DELETE"])
@auth.requiere_roles(*ROLES_STAFF)
def eliminar_equipo(id):
    param_hard = request.args.get("hard", "false").lower() == "true"
    logic.eliminar_equipo(id, hard_delete=param_hard)
    return "", 204


@equipos_bp.route("/<int:id>", methods=["GET", "PUT", "DELETE"])
def equipo_id_invalido(id):
    raise ValidationError(
        "El ID debe ser un número entero positivo."
    )