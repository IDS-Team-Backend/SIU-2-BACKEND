from flask import request, jsonify, Blueprint
import services.notas_service as logic
from config import DOCENTE, AYUDANTE
from utils.error_handlers import (
    created_response,
    ValidationError
)
from utils import auth_validator as auth

notas_bp = Blueprint("notas", __name__)
notas_bp.before_request(auth.validar_token)

@notas_bp.route("/", methods=["GET"])
def obtener_notas():
    evaluacion_id = request.args.get("evaluacion_id")
    alumno_id = request.args.get("alumno_id")
    equipo_id = request.args.get("equipo_id")
    notas, total = logic.obtener_notas(
        evaluacion_id,
        alumno_id,
        equipo_id
    )
    if not notas:
        return "", 204
    
    return jsonify({
        "notas": notas,
        "total": total
    }), 200

@notas_bp.route("/", methods=["POST"])
@auth.requiere_roles(DOCENTE, AYUDANTE)
def crear_nota():
    parametros = request.get_json()
    nueva_nota = logic.crear_nota(parametros)
    return created_response(
        {
            "message": "Nota creada exitosamente",
            "nota": nueva_nota
        },
        f"/notas/{nueva_nota['id']}"
    )

@notas_bp.route("/<int:id>", methods=["GET"])
def obtener_nota_por_id(id):
    nota = logic.obtener_nota_por_id(id)
    return jsonify(nota), 200

@notas_bp.route("/<int:id>", methods=["PATCH"])
@auth.requiere_roles(DOCENTE, AYUDANTE)
def reemplazar_nota(id):
    parametros = request.get_json()
    actualizado = logic.reemplazar_nota(
        id,
        parametros
    )
    if not actualizado:
        return {"error": "Nota no encontrada"}, 404
    return "", 204

@notas_bp.route("/<int:id>", methods=["DELETE"])
@auth.requiere_roles(DOCENTE)
def eliminar_nota(id):
    logic.eliminar_nota(id)
    return "", 204

@notas_bp.route("/<id>",methods=["GET", "PUT", "DELETE"])
def nota_id_invalido(id):
    raise ValidationError(
        "El ID debe ser un número entero positivo."
    )