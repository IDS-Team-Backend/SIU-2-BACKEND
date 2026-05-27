from flask import request, jsonify, Blueprint
import services.materias_service as logic
from config import ADMIN, DOCENTE, ALUMNO
from utils.error_handlers import created_response, ValidationError
from utils import auth_validator as auth
from utils import paginacion

materias_bp = Blueprint("materias", __name__)
materias_bp.before_request(auth.validar_token)

@materias_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"resource": "materias", "status": "healthy"}), 200

@materias_bp.route("/", methods=["GET"])
def obtener_materias():
    page, page_size, offset = paginacion.desde_request()

    nombre = request.args.get("nombre")
    codigo = request.args.get("codigo")

    materias, total = logic.obtener_materias(nombre, codigo, page_size, offset)

    if not materias:
        return "", 204

    return jsonify({
        "materias": materias,
        "total": total,
        "page": page,
        "page_size": page_size
    }), 200

@materias_bp.route("/", methods=["POST"])
@auth.requiere_roles(ADMIN)
def crear_materias():
    parametros = request.get_json(silent=True)

    if parametros is None:
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    new_materia = logic.crear_materias(parametros)

    return created_response({
        "message": "Materia creada exitosamente",
        "materia": new_materia
    }, f"/materias/{new_materia['id']}")

@materias_bp.route("/<int:materia_id>", methods=["GET"])
def obtener_materia_por_id(materia_id):
    materia = logic.obtener_materia_por_id(materia_id)
    return jsonify(materia), 200

@materias_bp.route("/<int:materia_id>", methods=["PUT"])
@auth.requiere_roles(ADMIN)
def reemplazar_materia(materia_id):
    parametros = request.get_json(silent=True)

    if parametros is None:
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    updated_materia = logic.reemplazar_materia(materia_id, parametros)

    return jsonify({
        "message": "Materia actualizada exitosamente",
        "materia": updated_materia
    }), 200

@materias_bp.route("/<int:materia_id>", methods=["DELETE"])
@auth.requiere_roles(ADMIN)
def eliminar_materia(materia_id: int):
    logic.eliminar_materia(materia_id)
    return "", 204

@materias_bp.route("/<int:materia_id>/cursos", methods=["GET"])
def obtener_cursos_de_materia(materia_id):
    page, page_size, offset = paginacion.desde_request()

    cursos, total = logic.obtener_cursos_de_materia(materia_id, page_size, offset)

    if not cursos:
        return "", 204

    return jsonify({
        "cursos": cursos,
        "total": total,
        "page": page,
        "page_size": page_size
    }), 200

@materias_bp.route("/<id>", methods=["GET", "PUT", "DELETE"])
def materia_id_invalido(id):
    raise ValidationError("El ID de materia debe ser un número entero positivo.")