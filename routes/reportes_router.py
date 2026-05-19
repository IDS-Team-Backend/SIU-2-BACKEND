from flask import Blueprint, jsonify

import services.reportes_service as logic


reportes_bp = Blueprint("reportes", __name__)


@reportes_bp.get("/health")
def health_check():
    return jsonify({"resource": "reportes", "status": "ok"})
