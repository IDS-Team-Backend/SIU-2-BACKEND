from flask import Blueprint, jsonify, request

from services import password_reset_service as logic
from utils import auth_validator as auth
from utils.error_handlers import ValidationError
from config import FRONTEND_URL

# Público: solicitar/confirmar reset (sin sesión).
password_bp = Blueprint("password", __name__)

# Privado: cambiar la propia contraseña (registrado en BLUEPRINTS_PRIVADOS).
password_private_bp = Blueprint("password_private", __name__)


@password_bp.post("/solicitar")
def solicitar():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()

    if not email:
        raise ValidationError("El email es obligatorio.")

    logic.solicitar_reset(email, FRONTEND_URL)

    return jsonify({
        "message": "Si el email está registrado, recibirás un enlace para restablecer tu contraseña."
    }), 200


@password_bp.post("/confirmar")
def confirmar():
    data = request.get_json(silent=True) or {}
    logic.confirmar_reset(
        token=data.get("token", "").strip(),
        nueva_password=data.get("nueva_password", ""),
        confirmar_password=data.get("confirmar_password", ""),
    )
    return jsonify({"message": "Contraseña actualizada correctamente."}), 200


@password_private_bp.post("/cambiar")
def cambiar():
    usuario_id = auth.obtener_usuario_id()
    data = request.get_json(silent=True) or {}
    logic.cambiar_password_autenticado(
        usuario_id=usuario_id,
        password_actual=data.get("password_actual", ""),
        nueva_password=data.get("nueva_password", ""),
        confirmar_password=data.get("confirmar_password", ""),
    )
    return jsonify({"message": "Contraseña cambiada correctamente."}), 200