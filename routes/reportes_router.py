from flask import Blueprint, jsonify
import services.reportes_service as logic
from utils import auth_validator as auth


reportes_bp = Blueprint("reportes", __name__)
reportes_bp.before_request(auth.validar_token)

@reportes_bp.get("/health")
def health_check():
    return jsonify({"resource": "reportes", "status": "ok"})
