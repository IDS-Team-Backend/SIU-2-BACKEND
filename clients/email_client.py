import io
import smtplib
from email.message import EmailMessage

from config import EMAIL_CONFIG
from utils.error_handlers import ValidationError

import qrcode

def send(to, subject, body, html=False, attachments=None):
    if not to:
        raise ValidationError("El destinatario es obligatorio")
    if not all([EMAIL_CONFIG["HOST"], EMAIL_CONFIG["SENDER"]]):
        raise ValidationError("La configuración de correo no está completa.")

    mensaje = EmailMessage()
    mensaje["From"]    = EMAIL_CONFIG["SENDER"]
    mensaje["To"]      = ", ".join(to) if isinstance(to, (list, tuple)) else to
    mensaje["Subject"] = subject

    if html:
        mensaje.set_content("Este correo requiere un cliente compatible con HTML.")
        mensaje.add_alternative(body, subtype="html")
    else:
        mensaje.set_content(body)

    # NUEVO: Procesamiento de archivos adjuntos
    if attachments:
        for adjunto in attachments:
            mensaje.add_attachment(
                adjunto["data"],
                maintype=adjunto.get("maintype", "application"),
                subtype=adjunto.get("subtype", "octet-stream"),
                cid=adjunto.get("cid"),
                filename=adjunto.get("filename"),
                disposition=adjunto.get("disposition", "attachment")
            )

    with smtplib.SMTP(EMAIL_CONFIG["HOST"], EMAIL_CONFIG["PORT"]) as smtp:
        smtp.ehlo()
        if EMAIL_CONFIG["USE_TLS"]:
            smtp.starttls()
            smtp.ehlo()
        if EMAIL_CONFIG["USERNAME"] and EMAIL_CONFIG["PASSWORD"]:
            try:
                smtp.login(EMAIL_CONFIG["USERNAME"], EMAIL_CONFIG["PASSWORD"])
            except smtplib.SMTPNotSupportedError:
                pass
        smtp.send_message(mensaje)

def enviar_finalizacion_registro_cuenta(to, nombre_usuario, apellido_usuario, url_registro, codigo, cuenta="usuario"):
    asunto = f"Finaliza tu registro en la FIUBA"

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; text-align: center; color: #333;">
        <h2>¡Hola, {nombre_usuario} {apellido_usuario}!</h2>
        <p>Recibimos una solicitud para finalizar tu registro como {cuenta} en la facultad <strong>FIUBA</strong>.</p>
        <p>Para completar tu registración, hacé click en el siguiente enlace y usá este código de verificación:</p>
        <a href="{url_registro}" style="display: inline-block; margin: 20px auto; padding: 10px 20px; background-color: #1e40af; color: white; text-decoration: none; border-radius: 5px;">Finalizar Registro</a>
        <h3 style="color: #1e40af;">Código de Verificación: {codigo}</h3>
        <p style="font-size: 12px; color: #777;">Si no solicitaste este registro, podés ignorar este correo.</p>
      </body>
    </html>
    """

    send(to=to, subject=asunto, body=html_body, html=True)

def enviar_email_bienvenida_estudiante_qr(to, nombre_alumno, apellido_alumno, token):
    # 1. Generar la imagen del QR
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(token)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")  # type: ignore
    img_buffer.seek(0)
    img_bytes = img_buffer.read()

    # 2. Preparar el texto y el asunto
    asunto = "Bienvenido/a a la FIUBA - Tu QR de asistencia"
    
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; text-align: center; color: #333;">
        <h2>¡Hola, {nombre_alumno} {apellido_alumno}!</h2>
        <p>Tu inscripción a la facultad <strong>FIUBA</strong> fue registrada exitosamente.</p>
        <p>Este es tu código QR personal para registrar asistencia. Guardalo, lo vas a usar en cada clase.
        Tambien lo podes ver desde la pagina SIU2.</p>
        <div style="margin: 20px auto; padding: 10px; width: 250px; border: 1px solid #ddd; border-radius: 8px;">
          <img src="cid:codigo_qr" alt="Código QR de Asistencia" width="250" height="250" />
        </div>
        <p style="font-size: 12px; color: #777;">Este código es único e intransferible.</p>
      </body>
    </html>
    """

    # 3. Empaquetar la imagen en un diccionario para la función send
    adjuntos = [{
        "data": img_bytes,
        "maintype": "image",
        "subtype": "png",
        "cid": "<codigo_qr>", # Al ponerle < > forzamos el Content-ID correctamente
        "filename": "codigo_qr.png",
        "disposition": "inline"
    }]

    # 4. Enviar el correo usando la función unificada
    send(to=to, subject=asunto, body=html_body, html=True, attachments=adjuntos)