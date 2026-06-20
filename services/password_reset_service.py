
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

import db
from repositories import usuarios_repository as usuarios_db
from utils.error_handlers import ValidationError, NotFoundError
import clients.email_client as email_client

TOKEN_EXPIRACION_HORAS = 1


def _crear_token_reset(usuario):
    """Genera un JWT firmado específico para reset de contraseña."""
    secret = current_app.config["JWT_SECRET_KEY"]
    payload = {
        "user_id":         usuario["id"],
        "email":           usuario["email"],
        "type":            "password_reset",
        # Los primeros 16 chars del hash actual — invalida el token si la contraseña cambia
        "pwd_hash_prefix": usuario["password_hash"][:16],
        "exp":             datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRACION_HORAS),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _verificar_token_reset(token):
    secret = current_app.config["JWT_SECRET_KEY"]
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValidationError("El enlace expiró. Solicitá uno nuevo.")
    except jwt.InvalidTokenError:
        raise ValidationError("El enlace es inválido.")

    if payload.get("type") != "password_reset":
        raise ValidationError("Token no válido para esta operación.")

    # FIX: consultar password_hash directamente
    fila = db.execute_query(
        "SELECT id, password_hash FROM usuarios WHERE id = %s AND deleted_at IS NULL",
        (payload["user_id"],),
        un_solo_valor=True,
    )
    if not fila:
        raise NotFoundError("Usuario no encontrado.")

    if not fila["password_hash"].startswith(payload["pwd_hash_prefix"]):
        raise ValidationError("El enlace ya fue utilizado. Solicitá uno nuevo.")

    return payload, fila

# Olvidé mi contraseña

def solicitar_reset(email, url_base_frontend):
    usuario = usuarios_db.get_user_by_email(email)
    if not usuario:
        return  # silencioso


    token = _crear_token_reset(usuario)
    url_reset = f"{url_base_frontend}/recuperar/confirmar?token={token}"

    try:
        email_client.send(
        to=usuario["email"],
        subject="Recuperación de contraseña — SIU-2",
        body=f"""
        <html><body style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto">
      <h2 style="color:#1e40af">Recuperar contraseña</h2>
      <p>Hola <strong>{usuario['nombre']}</strong>,</p>
      <p>Hacé clic en el enlace para restablecer tu contraseña:</p>
      <p><a href="{url_reset}" style="background:#1e40af;color:white;padding:12px 24px;
         text-decoration:none;border-radius:6px;font-weight:bold">
         Restablecer contraseña</a></p>
      <p style="font-size:13px;color:#666">Expira en {TOKEN_EXPIRACION_HORAS} hora.</p>
    </body></html>
    """,
    html=True,
        )
    except Exception as e:
        print(f"Error enviando email de recuperación: {e}")
        # No interrumpir el flujo, el usuario verá el mensaje genérico de éxito

def confirmar_reset(token, nueva_password, confirmar_password):
    if not nueva_password:
        raise ValidationError("La nueva contraseña es obligatoria.")
    if nueva_password != confirmar_password:
        raise ValidationError("Las contraseñas no coinciden.")
    if len(nueva_password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")

    payload, usuario = _verificar_token_reset(token)
    _actualizar_password(usuario["id"], nueva_password)


def cambiar_password_autenticado(usuario_id, password_actual, nueva_password, confirmar_password):
    if not password_actual:
        raise ValidationError("La contraseña actual es obligatoria.")
    if not nueva_password:
        raise ValidationError("La nueva contraseña es obligatoria.")
    if nueva_password != confirmar_password:
        raise ValidationError("Las contraseñas no coinciden.")
    if len(nueva_password) < 8:
        raise ValidationError("La nueva contraseña debe tener al menos 8 caracteres.")

    # Consultar hash directamente — obtener_usuario_por_id no lo incluye
    fila = db.execute_query(
        "SELECT id, password_hash FROM usuarios WHERE id = %s AND deleted_at IS NULL",
        (usuario_id,), un_solo_valor=True,
        )
    if not fila:
        raise NotFoundError("Usuario no encontrado.")

    if not check_password_hash(fila["password_hash"], password_actual):
        raise ValidationError("La contraseña actual es incorrecta.")

    _actualizar_password(usuario_id, nueva_password)


def _actualizar_password(usuario_id, nueva_password):
    nuevo_hash = generate_password_hash(nueva_password)
    db.execute_query(
        "UPDATE usuarios SET password_hash = %s WHERE id = %s",
        (nuevo_hash, usuario_id),
        modifica_db=True,
    )

