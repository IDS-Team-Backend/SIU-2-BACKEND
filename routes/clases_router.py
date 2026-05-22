from flask import Blueprint, jsonify, request
from utils import auth_validator as auth
import services.clases_service as logic


clases_bp = Blueprint("clases", __name__)
clases_bp.before_request(auth.validar_token)

@clases_bp.get("/")
def get_clases():

    filtros = {
        'status': request.args.get('status'),
        'profesor_id': request.args.get('profesor_id'),
        'curso_id': request.args.get('curso_id'),
        'fecha': request.args.get('fecha')
    }
    
    # se sacan los filtros que no se enviaron (value = None)
    filtros_limpios = {k: v for k, v in filtros.items() if v is not None}

    clases, total = logic.get_clases(filtros_limpios)

    return jsonify({"clases": clases, "total": total}), 200

@clases_bp.get("/<int:clase_id>")
def get_clase(clase_id):
    clase = logic.get_clase_by_id(clase_id)

    return jsonify({"clase": clase}), 200