from flask import Blueprint, jsonify

import services.alumnos_service as logic


alumnos_bp = Blueprint("alumnos", __name__)


@alumnos_bp.get("/health")
def health_check():
    return jsonify({"resource": "alumnos", "status": "ok"})
