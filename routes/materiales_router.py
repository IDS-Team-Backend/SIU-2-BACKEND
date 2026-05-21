from flask import Blueprint, jsonify
import services.materiales_service as logic


materiales_bp = Blueprint("materiales", __name__)

@materiales_bp.get("/health")
def health_check():
    return jsonify({"resource": "materiales", "status": "ok"})
