from datetime import datetime

from utils import validaciones
from utils.validaciones import construir_error_api


ANIO_INGRESO_MIN = 1900
CAMPOS_PATCH_PERMITIDOS = ("padron", "carrera", "anio_ingreso")


def _anio_ingreso_max():
    return datetime.now().year + 1

def _validar_carrera(body, errores, resultado, requerido=True):
    if "carrera" not in body and not requerido:
        return
    try:
        carrera = validaciones.validar_string_no_vacio(body.get("carrera"), "carrera")
        carrera = validaciones.validar_largo_string(carrera, 1, 150, "carrera")
        resultado["carrera"] = carrera
    except ValueError as e:
        errores.extend(e.args[0]["errors"])


def _validar_anio_ingreso(body, errores, resultado, requerido=True):
    if "anio_ingreso" not in body and not requerido:
        return
    try:
        anio_ingreso = validaciones.validar_entero(body.get("anio_ingreso"), "anio_ingreso")
        if anio_ingreso < ANIO_INGRESO_MIN or len(str(anio_ingreso)) != 4 or anio_ingreso > _anio_ingreso_max():
            raise ValueError("Año de ingreso inválido")
        resultado["anio_ingreso"] = anio_ingreso
    except ValueError as e:
        errores.extend(e.args)

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

def validar_body_registrar_alumno(body):
    validaciones.validar_body_presente(body)

    errores = []
    resultado = {}

    for campo in ("nombre", "apellido", "email"):
        try:
            resultado[campo] = validaciones.validar_string_no_vacio(body.get(campo), campo)
        except ValueError as e:
            errores.extend(e.args[0]["errors"])

    try:
        dni = validaciones.validar_entero(body.get("dni"), "dni")
        resultado["dni"] = validaciones.validar_minimo(dni, 1, "dni")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        padron = validaciones.validar_entero(body.get("padron"), "padron")
        resultado["padron"] = validaciones.validar_minimo(padron, 1, "padron")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    _validar_carrera(body, errores, resultado)
    _validar_anio_ingreso(body, errores, resultado)

    if errores:
        raise ValueError({"errors": errores})

    return resultado

def validar_body_reemplazar_estudiante(body):
    validaciones.validar_body_presente(body)

    errores = []
    padron = None
    carrera = None
    anio_ingreso = None

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
        "padron": padron,
        "carrera": carrera,
        "anio_ingreso": anio_ingreso,
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

    if errores:
        raise ValueError({"errors": errores})

    if not resultado:
        raise ValueError(construir_error_api(
            code="invalid.body",
            message="Debe enviar al menos un campo a modificar.",
            description="El body no contiene ningún campo válido.",
        ))

    return resultado
