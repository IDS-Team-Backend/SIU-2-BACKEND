from utils import validaciones
from utils.error_handlers import ValidationError


CAMPOS_PATCH_PERMITIDOS = ("legajo", "titulo", "departamento", "fecha_ingreso", "activo")


def _validar_usuario_id(body, errores, resultado):
    try:
        usuario_id = validaciones.validar_entero(body.get("usuario_id"), "usuario_id")
        resultado["usuario_id"] = validaciones.validar_minimo(usuario_id, 1, "usuario_id")
    except ValidationError as e:
        errores.append(str(e))


def _validar_legajo(body, errores, resultado, requerido=True):
    if "legajo" not in body and not requerido:
        return
    try:
        legajo = validaciones.validar_entero(body.get("legajo"), "legajo")
        resultado["legajo"] = validaciones.validar_minimo(legajo, 1, "legajo")
    except ValidationError as e:
        errores.append(str(e))


def _validar_titulo(body, errores, resultado, requerido=True):
    if "titulo" not in body and not requerido:
        return
    try:
        titulo = validaciones.validar_string_no_vacio(body.get("titulo"), "titulo")
        resultado["titulo"] = validaciones.validar_largo_string(titulo, 1, 150, "titulo")
    except ValidationError as e:
        errores.append(str(e))


def _validar_departamento(body, errores, resultado, requerido=True):
    if "departamento" not in body and not requerido:
        return
    try:
        departamento = validaciones.validar_string_no_vacio(body.get("departamento"), "departamento")
        resultado["departamento"] = validaciones.validar_largo_string(departamento, 1, 100, "departamento")
    except ValidationError as e:
        errores.append(str(e))


def _validar_fecha_ingreso(body, errores, resultado, requerido=True):
    if "fecha_ingreso" not in body and not requerido:
        return
    try:
        resultado["fecha_ingreso"] = validaciones.validar_fecha(
            body.get("fecha_ingreso"), "fecha_ingreso", permitir_futura=False
        )
    except ValidationError as e:
        errores.append(str(e))


def _validar_activo(body, errores, resultado, requerido=True):
    if "activo" not in body and not requerido:
        return
    try:
        resultado["activo"] = validaciones.validar_booleano(body.get("activo"), "activo")
    except ValidationError as e:
        errores.append(str(e))


def validar_body_crear_profesor(body):
    validaciones.validar_body_presente(body)

    errores = []
    resultado = {}

    _validar_usuario_id(body, errores, resultado)
    _validar_legajo(body, errores, resultado)
    _validar_titulo(body, errores, resultado)
    _validar_departamento(body, errores, resultado)
    _validar_fecha_ingreso(body, errores, resultado)

    if errores:
        raise ValidationError(errores)

    return resultado


def validar_body_reemplazar_profesor(body):
    validaciones.validar_body_presente(body)

    errores = []
    resultado = {}

    _validar_legajo(body, errores, resultado)
    _validar_titulo(body, errores, resultado)
    _validar_departamento(body, errores, resultado)
    _validar_fecha_ingreso(body, errores, resultado)
    _validar_activo(body, errores, resultado)

    if errores:
        raise ValidationError(errores)

    return resultado


def validar_body_modificar_profesor(body):
    validaciones.validar_body_presente(body)
    validaciones.validar_campos_permitidos(body, CAMPOS_PATCH_PERMITIDOS)

    errores = []
    resultado = {}

    _validar_legajo(body, errores, resultado, requerido=False)
    _validar_titulo(body, errores, resultado, requerido=False)
    _validar_departamento(body, errores, resultado, requerido=False)
    _validar_fecha_ingreso(body, errores, resultado, requerido=False)
    _validar_activo(body, errores, resultado, requerido=False)

    if errores:
        raise ValidationError(errores)

    if not resultado:
        raise ValidationError("Debe enviar al menos un campo a modificar.")

    return resultado
