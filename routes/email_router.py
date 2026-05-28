from flask import Blueprint, jsonify, request

import clients.email_client as email_client
from utils.error_handlers import ValidationError


email_bp = Blueprint("email", __name__)

# @email_bp.post("/send") para pruebas nomas, es peligroso exponer este endpoint xd
def send_email():
    data = request.get_json(silent=True) or {}

    to      = data.get("to")
    subject = data.get("subject")
    body    = data.get("body")
    html    = data.get("html", False)

    if not subject:
        raise ValidationError("El campo 'subject' es obligatorio")
    if not body:
        raise ValidationError("El campo 'body' es obligatorio")

    email_client.send(to=to, subject=subject, body=body, html=html)

    return jsonify({"status": "ok", "message": "Correo enviado"}), 200
