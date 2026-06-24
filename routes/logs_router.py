from flask import Blueprint, jsonify
from utils import auth_validator as auth
import services.logs_service as logic


logs_bp = Blueprint("logs", __name__)

@logs_bp.get("/health")
def health_check():
    return jsonify({"resource": "logs", "status": "ok"})
