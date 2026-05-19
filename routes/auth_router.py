from flask import Blueprint, jsonify

import services.auth_service as logic


auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/health")
def health_check():
    return jsonify({"resource": "auth", "status": "ok"})
