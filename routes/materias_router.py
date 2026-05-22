from flask import request, jsonify, Blueprint
import services.materias_service as logic
from utils.error_handlers import created_response, ValidationError


materias_bp = Blueprint('materias', __name__)

materias_params = ['nombre']

@materias_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"resource": "materias", "status": "healthy"}), 200

@materias_bp.route('/', methods=['GET'])
def obtener_materias():
    nombre = request.args.get('nombre')
    codigo = request.args.get('codigo')

    materias, total = logic.obtener_materias( nombre, codigo)

    if not materias:
        return "", 204
    
    return jsonify({"materias": materias, "total": total}), 200

#---------POST / materias--------------

@materias_bp.route('/', methods=['POST'])
def crear_materias():
    parametros = request.get_json(silent=True)
    if parametros is None:
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    new_materia = logic.crear_materias(parametros)
    return created_response({
        "message": "Materia creada exitosamente",
        "materia": new_materia},
        f"/materias/{new_materia['id']}")


# ---------- GET /materias/{id} ----------
@materias_bp.route("/<int:materia_id>", methods=["GET"])
def obtener_materia_por_id(materia_id):
    materia = logic.obtener_materia_por_id(materia_id)
    return jsonify(materia), 200


# ---------- PUT /materias/{id} ----------
@materias_bp.route("/<int:materia_id>", methods=["PUT"])
def reemplazar_materia(materia_id):
    parametros = request.get_json(silent=True)
    if parametros is None:
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    updated_materia = logic.reemplazar_materia(materia_id, parametros)

    if not updated_materia:
        return jsonify({"error": "Materia no encontrada"}), 404

    return jsonify({
        "message": "Materia actualizada exitosamente",
        "materia": updated_materia
    }), 200


# ---------- DELETE /materias/{id} ----------
@materias_bp.route("/<int:materia_id>", methods=["DELETE"])
def eliminar_materia(materia_id: int):
    logic.eliminar_materia(materia_id)
    return "", 204


# ---------- GET /materias/{id}/cursos ----------
@materias_bp.route("/<int:materia_id>/cursos", methods=["GET"])
def obtener_cursos_de_materia(materia_id):
    cursos, total = logic.obtener_cursos_de_materia(materia_id)

    if not cursos:
        return "", 204

    return jsonify({"cursos": cursos, "total": total}), 200


# ---------- Catch-all para IDs no numéricos ----------
@materias_bp.route("/<id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def materia_id_invalido(id):
    raise ValidationError("El ID debe ser un número entero positivo.")