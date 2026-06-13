import secrets
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

import db
import repositories.usuarios_repository as usuarios_db
import repositories.profesores_repository as profesores_db
import repositories.verificacion_registro_repository as verificacion_db
import clients.email_client as email_client
from services.auth_service import validar_datos_usuario
from utils.error_handlers import ValidationError, DuplicateError

CODIGO_EXPIRACION_HORAS = 24


def _generar_codigo():
    return f"{secrets.randbelow(1_000_000):06d}"


def _generar_y_enviar_codigo(usuario, url_base_frontend):
    """Genera un OTP, guarda su hash y envía el email para finalizar la registración."""
    codigo = _generar_codigo()
    expira = datetime.now() + timedelta(hours=CODIGO_EXPIRACION_HORAS)
    verificacion_db.crear(usuario["id"], generate_password_hash(codigo), expira)

    # Útil en dev cuando no hay SMTP configurado: el código queda en consola.
    print(f"[REGISTRO] OTP para {usuario['email']}: {codigo}")

    url_finalizar = f"{url_base_frontend}/finalizar-registracion?email={usuario['email']}"
    try:
        email_client.send(
            to=usuario["email"],
            subject="Finalizá tu registración — SIU-2",
            body=f"""
            <html><body style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto">
          <h2 style="color:#1e40af">Bienvenido/a, {usuario['nombre']}</h2>
          <p>Se creó tu cuenta de profesor. Para activarla, ingresá este código y definí tu contraseña:</p>
          <p style="font-size:28px;font-weight:bold;letter-spacing:6px;color:#1e40af">{codigo}</p>
          <p><a href="{url_finalizar}" style="background:#1e40af;color:white;padding:12px 24px;
             text-decoration:none;border-radius:6px;font-weight:bold">Finalizar registración</a></p>
          <p style="font-size:13px;color:#666">El código expira en {CODIGO_EXPIRACION_HORAS} horas.</p>
        </body></html>
        """,
            html=True,
        )
    except Exception as e:
        # No interrumpir el alta: el código ya quedó impreso en consola para dev.
        print(f"Error enviando email de registración: {e}")


def registrar_profesor(parametros, url_base_frontend):
    """Crea usuario (sin contraseña usable) + perfil profesor y dispara el OTP."""
    nombre = parametros["nombre"]
    apellido = parametros["apellido"]
    email = parametros["email"]
    dni = parametros["dni"]
    legajo = parametros["legajo"]
    titulo = parametros["titulo"]
    departamento = parametros["departamento"]
    fecha_ingreso = parametros["fecha_ingreso"]

    # Contraseña aleatoria: la cuenta no es usable hasta que el profesor finalice la registración.
    password_placeholder = secrets.token_urlsafe(16)

    # 1. Validar todo ANTES de insertar (no hay transacción multi-statement).
    validar_datos_usuario(nombre, apellido, dni, email, password_placeholder)

    # 2. Unicidad.
    if usuarios_db.existe_email(email):
        raise DuplicateError("Ya existe un usuario con ese email.")
    if usuarios_db.existe_dni(dni):
        raise DuplicateError("Ya existe un usuario con ese DNI.")
    if profesores_db.existe_legajo(legajo):
        raise DuplicateError("Ya existe un profesor con ese legajo.")

    # 3. Crear usuario pendiente de verificación.
    usuario = usuarios_db.crear_usuario(
        nombre, apellido, email, dni, password_placeholder,
        es_admin=False, email_verificado=False,
    )

    # 4. Crear perfil profesor; si falla, limpiar el usuario huérfano.
    try:
        profesor = profesores_db.crear_profesor(
            usuario["id"], legajo, titulo, departamento, fecha_ingreso
        )
    except Exception:
        usuarios_db.eliminar_usuario(usuario["id"])
        raise

    # 5. Enviar el OTP de finalización.
    _generar_y_enviar_codigo(usuario, url_base_frontend)

    return profesor


def finalizar_registro(email, codigo, nueva_password, confirmar_password):
    email = (email or "").strip()
    codigo = (codigo or "").strip()

    if not email or not codigo:
        raise ValidationError("El email y el código son obligatorios.")
    if not nueva_password:
        raise ValidationError("La nueva contraseña es obligatoria.")
    if nueva_password != confirmar_password:
        raise ValidationError("Las contraseñas no coinciden.")
    if len(nueva_password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")

    usuario = usuarios_db.get_user_by_email(email)
    if not usuario:
        raise ValidationError("No encontramos una registración pendiente para ese email.")
    if usuario["email_verificado"]:
        raise ValidationError("Esta cuenta ya fue verificada. Podés iniciar sesión.")

    verificacion = verificacion_db.obtener_vigente_por_usuario(usuario["id"])
    if not verificacion:
        raise ValidationError("El código expiró o no existe. Pedí que te reenvíen uno.")
    if not check_password_hash(verificacion["codigo"], codigo):
        raise ValidationError("El código es incorrecto.")

    db.execute_query(
        "UPDATE usuarios SET password_hash = %s, email_verificado = TRUE WHERE id = %s",
        (generate_password_hash(nueva_password), usuario["id"]),
        modifica_db=True,
    )
    verificacion_db.marcar_consumido(verificacion["id"])
