from flask import Blueprint, jsonify

import services.equipos_service as logic


equipos_bp = Blueprint("equipos", __name__)


@equipos_bp.get("/health")
def health_check():
    return jsonify({"resource": "equipos", "status": "ok"})
