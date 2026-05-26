from utils import validaciones
from utils.validaciones import construir_error_api


CAMPOS_PATCH_PERMITIDOS = ("legajo", "titulo", "departamento", "fecha_ingreso", "activo")


def _validar_legajo(body, errores, resultado, requerido=True):
    if "legajo" not in body and not requerido:
        return
    try:
        legajo = validaciones.validar_entero(body.get("legajo"), "legajo")
        legajo = validaciones.validar_minimo(legajo, 1, "legajo")
        resultado["legajo"] = legajo
    except ValueError as e:
        errores.extend(e.args[0]["errors"])


def _validar_titulo(body, errores, resultado, requerido=True):
    if "titulo" not in body and not requerido:
        return
    try:
        titulo = validaciones.validar_string_no_vacio(body.get("titulo"), "titulo")
        titulo = validaciones.validar_largo_string(titulo, 1, 150, "titulo")
        resultado["titulo"] = titulo
    except ValueError as e:
        errores.extend(e.args[0]["errors"])


def _validar_departamento(body, errores, resultado, requerido=True):
    if "departamento" not in body and not requerido:
        return
    try:
        departamento = validaciones.validar_string_no_vacio(body.get("departamento"), "departamento")
        departamento = validaciones.validar_largo_string(departamento, 1, 100, "departamento")
        resultado["departamento"] = departamento
    except ValueError as e:
        errores.extend(e.args[0]["errors"])


def _validar_fecha_ingreso(body, errores, resultado, requerido=True):
    if "fecha_ingreso" not in body and not requerido:
        return
    try:
        resultado["fecha_ingreso"] = validaciones.validar_fecha_iso(
            body.get("fecha_ingreso"), "fecha_ingreso", permitir_futura=False
        )
    except ValueError as e:
        errores.extend(e.args[0]["errors"])


def _validar_activo(body, errores, resultado, requerido=True):
    if "activo" not in body and not requerido:
        return
    try:
        resultado["activo"] = validaciones.validar_booleano(body.get("activo"), "activo")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])


def validar_body_crear_profesor(body):
    validaciones.validar_body_presente(body)

    errores = []
    resultado = {}

    try:
        usuario_id = validaciones.validar_entero(body.get("usuario_id"), "usuario_id")
        usuario_id = validaciones.validar_minimo(usuario_id, 1, "usuario_id")
        resultado["usuario_id"] = usuario_id
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    _validar_legajo(body, errores, resultado)
    _validar_titulo(body, errores, resultado)
    _validar_departamento(body, errores, resultado)
    _validar_fecha_ingreso(body, errores, resultado)

    if errores:
        raise ValueError({"errors": errores})

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
        raise ValueError({"errors": errores})

    return resultado


def validar_body_modificar_profesor(body):
    validaciones.validar_body_presente(body)

    extras = set(body.keys()) - set(CAMPOS_PATCH_PERMITIDOS)
    if extras:
        raise ValueError(construir_error_api(
            code="invalid.body",
            message="Campos no permitidos en el body.",
            description=(
                f"Los campos {sorted(extras)} no son válidos. "
                f"Campos permitidos: {', '.join(CAMPOS_PATCH_PERMITIDOS)}."
            ),
        ))

    errores = []
    resultado = {}

    _validar_legajo(body, errores, resultado, requerido=False)
    _validar_titulo(body, errores, resultado, requerido=False)
    _validar_departamento(body, errores, resultado, requerido=False)
    _validar_fecha_ingreso(body, errores, resultado, requerido=False)
    _validar_activo(body, errores, resultado, requerido=False)

    if errores:
        raise ValueError({"errors": errores})

    if not resultado:
        raise ValueError(construir_error_api(
            code="invalid.body",
            message="Debe enviar al menos un campo a modificar.",
            description="El body no contiene ningún campo válido.",
        ))

    return resultado
