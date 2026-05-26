from datetime import datetime

from utils import validaciones
from utils.validaciones import construir_error_api


ANIO_INGRESO_MIN = 1900
CAMPOS_PATCH_PERMITIDOS = ("padron", "carrera", "anio_ingreso", "activo")


def _anio_ingreso_max():
    return datetime.now().year + 1


def validar_body_crear_estudiante(body):
    validaciones.validar_body_presente(body)

    errores = []
    usuario_id = None
    padron = None
    carrera = None
    anio_ingreso = None

    try:
        usuario_id = validaciones.validar_entero(body.get("usuario_id"), "usuario_id")
        usuario_id = validaciones.validar_minimo(usuario_id, 1, "usuario_id")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        padron = validaciones.validar_entero(body.get("padron"), "padron")
        padron = validaciones.validar_minimo(padron, 1, "padron")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        carrera = validaciones.validar_string_no_vacio(body.get("carrera"), "carrera")
        carrera = validaciones.validar_largo_string(carrera, 1, 150, "carrera")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        anio_ingreso = validaciones.validar_entero(body.get("anio_ingreso"), "anio_ingreso")
        anio_ingreso = validaciones.validar_minimo(anio_ingreso, ANIO_INGRESO_MIN, "anio_ingreso")
        anio_ingreso = validaciones.validar_maximo(anio_ingreso, _anio_ingreso_max(), "anio_ingreso")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    if errores:
        raise ValueError({"errors": errores})

    return {
        "usuario_id": usuario_id,
        "padron": padron,
        "carrera": carrera,
        "anio_ingreso": anio_ingreso,
    }


def validar_body_reemplazar_estudiante(body):
    validaciones.validar_body_presente(body)

    errores = []
    padron = None
    carrera = None
    anio_ingreso = None
    activo = None

    try:
        padron = validaciones.validar_entero(body.get("padron"), "padron")
        padron = validaciones.validar_minimo(padron, 1, "padron")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        carrera = validaciones.validar_string_no_vacio(body.get("carrera"), "carrera")
        carrera = validaciones.validar_largo_string(carrera, 1, 150, "carrera")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        anio_ingreso = validaciones.validar_entero(body.get("anio_ingreso"), "anio_ingreso")
        anio_ingreso = validaciones.validar_minimo(anio_ingreso, ANIO_INGRESO_MIN, "anio_ingreso")
        anio_ingreso = validaciones.validar_maximo(anio_ingreso, _anio_ingreso_max(), "anio_ingreso")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        activo = validaciones.validar_booleano(body.get("activo"), "activo")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    if errores:
        raise ValueError({"errors": errores})

    return {
        "padron": padron,
        "carrera": carrera,
        "anio_ingreso": anio_ingreso,
        "activo": activo,
    }


def validar_body_modificar_estudiante(body):
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

    if "padron" in body:
        try:
            padron = validaciones.validar_entero(body.get("padron"), "padron")
            padron = validaciones.validar_minimo(padron, 1, "padron")
            resultado["padron"] = padron
        except ValueError as e:
            errores.extend(e.args[0]["errors"])

    if "carrera" in body:
        try:
            carrera = validaciones.validar_string_no_vacio(body.get("carrera"), "carrera")
            carrera = validaciones.validar_largo_string(carrera, 1, 150, "carrera")
            resultado["carrera"] = carrera
        except ValueError as e:
            errores.extend(e.args[0]["errors"])

    if "anio_ingreso" in body:
        try:
            anio_ingreso = validaciones.validar_entero(body.get("anio_ingreso"), "anio_ingreso")
            anio_ingreso = validaciones.validar_minimo(anio_ingreso, ANIO_INGRESO_MIN, "anio_ingreso")
            anio_ingreso = validaciones.validar_maximo(anio_ingreso, _anio_ingreso_max(), "anio_ingreso")
            resultado["anio_ingreso"] = anio_ingreso
        except ValueError as e:
            errores.extend(e.args[0]["errors"])

    if "activo" in body:
        try:
            resultado["activo"] = validaciones.validar_booleano(body.get("activo"), "activo")
        except ValueError as e:
            errores.extend(e.args[0]["errors"])

    if errores:
        raise ValueError({"errors": errores})

    if not resultado:
        raise ValueError(construir_error_api(
            code="invalid.body",
            message="Debe enviar al menos un campo a modificar.",
            description="El body no contiene ningún campo válido.",
        ))

    return resultado
