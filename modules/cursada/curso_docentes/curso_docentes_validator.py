from utils import validaciones
from config import ROLES_DOCENTE_CATEDRA


def _validar_rol(body, errores, resultado):
    rol = body.get("nombre") or body.get("rol")
    if rol not in ROLES_DOCENTE_CATEDRA:
        errores.extend(validaciones.construir_error_api(
            code="invalid.nombre",
            message="Tipo de participación inválido.",
            description=f"Debe ser uno de: {', '.join(ROLES_DOCENTE_CATEDRA)}.",
        )["errors"])
    else:
        resultado["rol"] = rol


def validar_body_agregar_integrante(body):
    validaciones.validar_body_presente(body)

    errores = []
    resultado = {}

    for campo in ("curso_id", "docente_id"):
        try:
            valor = validaciones.validar_entero(body.get(campo), campo)
            resultado[campo] = validaciones.validar_minimo(valor, 1, campo)
        except ValueError as e:
            errores.extend(e.args[0]["errors"])

    _validar_rol(body, errores, resultado)

    if errores:
        raise ValueError({"errors": errores})

    return resultado


def validar_body_cambiar_participacion(body):
    validaciones.validar_body_presente(body)

    errores = []
    resultado = {}

    _validar_rol(body, errores, resultado)

    if errores:
        raise ValueError({"errors": errores})

    return resultado
