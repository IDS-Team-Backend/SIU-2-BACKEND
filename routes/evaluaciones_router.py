from flask import Blueprint, jsonify

import services.evaluaciones_service as logic


evaluaciones_bp = Blueprint("evaluaciones", __name__)


@evaluaciones_bp.get("/health")
def health_check():
    return jsonify({"resource": "evaluaciones", "status": "ok"})
