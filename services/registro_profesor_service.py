import secrets
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

import db
import repositories.usuarios_repository as usuarios_db
import repositories.profesores_repository as profesores_db
import repositories.verificacion_registro_repository as verificacion_db
from utils.error_handlers import ValidationError, DuplicateError
import services.estudiantes_service as estudiantes_logic
import clients.email_client as EmailClient
import services.usuarios_service as usuarios_logic
import repositories.estudiantes_repository as estudiantes_db

CODIGO_EXPIRACION_HORAS = 24


def _generar_codigo():
    return f"{secrets.randbelow(1_000_000):06d}"


def _generar_y_enviar_codigo(usuario, url_base_frontend, cuenta="usuario"):
    """Genera un OTP, guarda su hash y envía el email para finalizar la registración."""
    codigo = _generar_codigo()
    expira = datetime.now() + timedelta(hours=CODIGO_EXPIRACION_HORAS)
    verificacion_db.crear(usuario["id"], generate_password_hash(codigo), expira)

    # Útil en dev cuando no hay SMTP configurado: el código queda en consola.
    print(f"[REGISTRO] OTP para {usuario['email']}: {codigo}")

    url_finalizar_registro = f"{url_base_frontend}/finalizar-registracion?email={usuario['email']}&codigo={codigo}"
    try:
        EmailClient.enviar_finalizacion_registro_cuenta(
            to=usuario["email"],
            nombre_usuario=usuario["nombre"],
            apellido_usuario=usuario["apellido"],
            url_registro=url_finalizar_registro,
            codigo=codigo,
            cuenta=cuenta
        )
    except Exception as e:
        # No interrumpir el alta: el código ya quedó impreso en consola para dev.
        print(f"Error enviando email de registración: {e}")

def registrar_alumno(parametros, url_base_frontend):
    """Crea usuario (sin contraseña usable) + perfil alumno y dispara el email de bienvenida."""
    # Contraseña aleatoria: la cuenta no es usable hasta que el alumno finalice la registración.
    password_placeholder = secrets.token_urlsafe(16)
    parametros["password"] = password_placeholder

    # 3. Crear usuario.
    usuario = usuarios_logic.crear_usuario(parametros)

    parametros["usuario_id"] = usuario["id"]
    # 4. Crear perfil alumno; si falla, limpiar el usuario huérfano.
    try:
        alumno = estudiantes_logic.crear_estudiante(parametros)
    except Exception:
        usuarios_db.eliminar_usuario(usuario["id"])
        raise

    _generar_y_enviar_codigo(usuario, url_base_frontend, cuenta="estudiante")

    return alumno


def registrar_profesor(parametros, url_base_frontend):
    """Crea usuario (sin contraseña usable) + perfil profesor y dispara el OTP."""
    legajo = parametros["legajo"]
    titulo = parametros["titulo"]
    departamento = parametros["departamento"]
    fecha_ingreso = parametros["fecha_ingreso"]

    # Contraseña aleatoria: la cuenta no es usable hasta que el profesor finalice la registración.
    password_placeholder = secrets.token_urlsafe(16)
    parametros["password"] = password_placeholder

    # 2. Unicidad.
    if profesores_db.existe_legajo(legajo):
        raise DuplicateError("Ya existe un profesor con ese legajo.")

    # 3. Crear usuario pendiente de verificación.
    usuario = usuarios_logic.crear_usuario(parametros)

    # 4. Crear perfil profesor; si falla, limpiar el usuario huérfano.
    try:
        profesor = profesores_db.crear_profesor(
            usuario["id"], legajo, titulo, departamento, fecha_ingreso
        )
    except Exception:
        usuarios_db.eliminar_usuario(usuario["id"])
        raise

    # 5. Enviar el OTP de finalización.
    _generar_y_enviar_codigo(usuario, url_base_frontend, cuenta="profesor")

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


    estudiante = estudiantes_db.obtener_estudiante_por_usuario_id(usuario["id"])
    if estudiante:
        EmailClient.enviar_email_bienvenida_estudiante_qr(
            to=usuario["email"],
            nombre_alumno=usuario["nombre"],
            apellido_alumno=usuario["apellido"],
            token=estudiante["token_qr"],
        )
    
    verificacion_db.marcar_consumido(verificacion["id"])
