from utils import validaciones
from utils.validaciones import construir_error_api


ESTADOS_PERMITIDOS = ("activo", "abandono")
CAMPOS_PATCH_PERMITIDOS = ("estudiante_id", "curso_id", "estado")


def _validar_estado(valor):
    if valor not in ESTADOS_PERMITIDOS:
        raise ValueError(construir_error_api(
            code="invalid.estado",
            message="Estado inválido.",
            description=(
                f"El campo 'estado' debe ser uno de: {', '.join(ESTADOS_PERMITIDOS)}. "
                f"Se recibió: {valor!r}."
            ),
        ))
    return valor


def validar_body_crear_estudiante_curso(body):
    validaciones.validar_body_presente(body)

    errores = []
    estudiante_id = None
    curso_id = None
    estado = None

    try:
        estudiante_id = validaciones.validar_entero(body.get("estudiante_id"), "estudiante_id")
        estudiante_id = validaciones.validar_minimo(estudiante_id, 1, "estudiante_id")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        curso_id = validaciones.validar_entero(body.get("curso_id"), "curso_id")
        curso_id = validaciones.validar_minimo(curso_id, 1, "curso_id")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        estado = _validar_estado(body.get("estado", "activo"))
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    if errores:
        raise ValueError({"errors": errores})

    return {
        "estudiante_id": estudiante_id,
        "curso_id": curso_id,
        "estado": estado,
    }


def validar_body_reemplazar_estudiante_curso(body):
    validaciones.validar_body_presente(body)

    errores = []
    estudiante_id = None
    curso_id = None
    estado = None

    try:
        estudiante_id = validaciones.validar_entero(body.get("estudiante_id"), "estudiante_id")
        estudiante_id = validaciones.validar_minimo(estudiante_id, 1, "estudiante_id")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        curso_id = validaciones.validar_entero(body.get("curso_id"), "curso_id")
        curso_id = validaciones.validar_minimo(curso_id, 1, "curso_id")
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        estado = _validar_estado(body.get("estado"))
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    if errores:
        raise ValueError({"errors": errores})

    return {
        "estudiante_id": estudiante_id,
        "curso_id": curso_id,
        "estado": estado,
    }


def validar_body_modificar_estudiante_curso(body):
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

    if "estudiante_id" in body:
        try:
            estudiante_id = validaciones.validar_entero(body.get("estudiante_id"), "estudiante_id")
            estudiante_id = validaciones.validar_minimo(estudiante_id, 1, "estudiante_id")
            resultado["estudiante_id"] = estudiante_id
        except ValueError as e:
            errores.extend(e.args[0]["errors"])

    if "curso_id" in body:
        try:
            curso_id = validaciones.validar_entero(body.get("curso_id"), "curso_id")
            curso_id = validaciones.validar_minimo(curso_id, 1, "curso_id")
            resultado["curso_id"] = curso_id
        except ValueError as e:
            errores.extend(e.args[0]["errors"])

    if "estado" in body:
        try:
            resultado["estado"] = _validar_estado(body.get("estado"))
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
