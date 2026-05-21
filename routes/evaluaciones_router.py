from flask import Blueprint, jsonify
from utils import auth_validator as auth
import services.evaluaciones_service as logic


evaluaciones_bp = Blueprint("evaluaciones", __name__)
evaluaciones_bp.before_request(auth.validar_token)

@evaluaciones_bp.get("/health")
def health_check():
    return jsonify({"resource": "evaluaciones", "status": "ok"})
