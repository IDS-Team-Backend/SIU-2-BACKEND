from flask import Blueprint, jsonify
from utils import auth_validator as auth
import services.equipos_service as logic


equipos_bp = Blueprint("equipos", __name__)
equipos_bp.before_request(auth.validar_token)

@equipos_bp.get("/health")
def health_check():
    return jsonify({"resource": "equipos", "status": "ok"})
