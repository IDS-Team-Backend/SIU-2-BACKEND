from flask import Blueprint, jsonify
from utils import auth_validator as auth
import services.asistencia_service as logic


asistencia_bp = Blueprint("asistencia", __name__)

@asistencia_bp.get("/health")
def health_check():
    return jsonify({"resource": "asistencia", "status": "ok"})
