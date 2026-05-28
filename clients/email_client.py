import io
import smtplib
from email.message import EmailMessage

from config import EMAIL_CONFIG
from utils.error_handlers import ValidationError

import qrcode

def send(to, subject, body, html=False):
    if not to:
        raise ValidationError("El destinatario es obligatorio")
    if not all([EMAIL_CONFIG["HOST"], EMAIL_CONFIG["USERNAME"], EMAIL_CONFIG["PASSWORD"], EMAIL_CONFIG["SENDER"]]):
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

    with smtplib.SMTP(EMAIL_CONFIG["HOST"], EMAIL_CONFIG["PORT"]) as smtp:
        if EMAIL_CONFIG["USE_TLS"]:
            smtp.starttls()
        smtp.login(EMAIL_CONFIG["USERNAME"], EMAIL_CONFIG["PASSWORD"])
        smtp.send_message(mensaje)

def enviar_email_qr(to, subject, nombre_alumno, apellido_alumno, clase_nombre, token, expiracion):
    if not to:
        raise ValidationError("El destinatario es obligatorio")
    if not all([EMAIL_CONFIG["HOST"], EMAIL_CONFIG["USERNAME"], EMAIL_CONFIG["PASSWORD"], EMAIL_CONFIG["SENDER"]]):
        raise ValidationError("La configuración de correo no está completa.")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4) # se define la estructura del qr
    qr.add_data(token)  # se le mete el token
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white") # se crea la imagen del qr
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG") # type: ignore
    img_buffer.seek(0)
    img_bytes = img_buffer.read()

    mensaje = EmailMessage()
    mensaje["From"] = EMAIL_CONFIG["SENDER"]
    mensaje["To"] = ", ".join(to) if isinstance(to, (list, tuple)) else to
    mensaje["Subject"] = subject

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; text-align: center; color: #333;">
        <h2>¡Hola, {nombre_alumno}!</h2>
        <p>Acá tenés tu código QR para registrar la asistencia en la clase: <strong>{clase_nombre}</strong>.</p>
        <div style="margin: 20px auto; padding: 10px; width: 250px; border: 1px solid #ddd; border-radius: 8px;">
          <img src="cid:codigo_qr" alt="Código QR de Asistencia" width="250" height="250" />
        </div>
        <p style="font-size: 12px; color: #777;">Este código es de uso único y dinámico.</p>
      </body>
    </html>
    """

    mensaje.set_content("Tu cliente de correo no soporta HTML. Tu token es: " + token)
    mensaje.add_alternative(html_body, subtype="html")

    mensaje.add_attachment(
            img_bytes,
            maintype="image",
            subtype="png",
            cid="codigo_qr",
            filename="codigo_qr.png",
            disposition="inline"
        )

    with smtplib.SMTP(EMAIL_CONFIG["HOST"], EMAIL_CONFIG["PORT"]) as smtp:
        if EMAIL_CONFIG["USE_TLS"]:
            smtp.starttls()
        smtp.login(EMAIL_CONFIG["USERNAME"], EMAIL_CONFIG["PASSWORD"])
        smtp.send_message(mensaje)