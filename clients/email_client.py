import smtplib
from email.message import EmailMessage

from config import EmailConfig
from utils.error_handlers import ValidationError


class EmailClient:
    def send(self, to, subject, body, html=False):
        if not to:
            raise ValidationError("El destinatario es obligatorio")

        mensaje = EmailMessage()
        mensaje["From"]    = EmailConfig.SENDER
        mensaje["To"]      = ", ".join(to) if isinstance(to, (list, tuple)) else to
        mensaje["Subject"] = subject

        if html:
            mensaje.set_content("Este correo requiere un cliente compatible con HTML.")
            mensaje.add_alternative(body, subtype="html")
        else:
            mensaje.set_content(body)

        with smtplib.SMTP(EmailConfig.HOST, EmailConfig.PORT) as smtp:
            if EmailConfig.USE_TLS:
                smtp.starttls()
            smtp.login(EmailConfig.USERNAME, EmailConfig.PASSWORD)
            smtp.send_message(mensaje)
