import smtplib
from email.message import EmailMessage

from config import EMAIL_CONFIG
from utils.error_handlers import ValidationError


class EmailClient:
    def send(self, to, subject, body, html=False):
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
