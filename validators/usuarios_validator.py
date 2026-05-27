from utils import validaciones
from utils.error_handlers import ValidationError


DNI_DIGITOS = 8
PASSWORD_MIN_LARGO = 6


def _validar_dni_login(body, errores, resultado):
    dni = body.get("dni")
    if not isinstance(dni, int) or isinstance(dni, bool):
        errores.append("El DNI debe ser un número entero.")
        return
    resultado["dni"] = dni


def _validar_dni_signup(body, errores, resultado):
    dni = body.get("dni")
    if not isinstance(dni, int) or isinstance(dni, bool) or dni <= 0 or len(str(dni)) != DNI_DIGITOS:
        errores.append(f"El DNI debe ser un número entero de {DNI_DIGITOS} dígitos.")
        return
    resultado["dni"] = dni


def _validar_password_login(body, errores, resultado):
    password = body.get("password")
    if not isinstance(password, str) or not password:
        errores.append("La contraseña es obligatoria.")
        return
    resultado["password"] = password


def _validar_password_signup(body, errores, resultado):
    password = body.get("password")
    if not isinstance(password, str) or len(password) < PASSWORD_MIN_LARGO:
        errores.append(f"La contraseña debe tener al menos {PASSWORD_MIN_LARGO} caracteres.")
        return
    resultado["password"] = password


def _validar_email(body, errores, resultado):
    try:
        resultado["email"] = validaciones.validar_email(body.get("email"), "email")
    except ValidationError as e:
        errores.append(str(e))


def _validar_nombre(body, errores, resultado):
    try:
        nombre = validaciones.validar_string_no_vacio(body.get("nombre"), "nombre")
        resultado["nombre"] = validaciones.validar_largo_string(nombre, 1, 100, "nombre")
    except ValidationError as e:
        errores.append(str(e))


def _validar_apellido(body, errores, resultado):
    try:
        apellido = validaciones.validar_string_no_vacio(body.get("apellido"), "apellido")
        resultado["apellido"] = validaciones.validar_largo_string(apellido, 1, 100, "apellido")
    except ValidationError as e:
        errores.append(str(e))


def validar_body_login(body):
    validaciones.validar_body_presente(body)

    errores = []
    resultado = {}

    _validar_dni_login(body, errores, resultado)
    _validar_password_login(body, errores, resultado)

    if errores:
        raise ValidationError(errores)

    return resultado


def validar_body_signup(body):
    validaciones.validar_body_presente(body)

    errores = []
    resultado = {}

    _validar_nombre(body, errores, resultado)
    _validar_apellido(body, errores, resultado)
    _validar_dni_signup(body, errores, resultado)
    _validar_email(body, errores, resultado)
    _validar_password_signup(body, errores, resultado)

    if errores:
        raise ValidationError(errores)

    return resultado
