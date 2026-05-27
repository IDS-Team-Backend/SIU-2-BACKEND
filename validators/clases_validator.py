from config import ESTADOS_CLASE
from utils import validaciones
from utils.error_handlers import ValidationError


CAMPOS_OBLIGATORIOS = ("nombre", "profesor_id", "curso_id", "fecha_hora_inicio", "fecha_hora_fin")
CAMPOS_OPCIONALES = ("tema", "status")
CAMPOS_PERMITIDOS = CAMPOS_OBLIGATORIOS + CAMPOS_OPCIONALES
FILTROS_PERMITIDOS = ("status", "profesor_id", "curso_id", "fecha", "activa")


def _strip_strings(body):
    return {
        k: (v.strip() if isinstance(v, str) else v)
        for k, v in body.items()
    }


def _validar_obligatorios(body, errores):
    for campo in CAMPOS_OBLIGATORIOS:
        valor = body.get(campo)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            errores.append(f"El campo '{campo}' es obligatorio.")


def _validar_extras(body, errores):
    extras = set(body.keys()) - set(CAMPOS_PERMITIDOS)
    for campo in sorted(extras):
        errores.append(f"El campo '{campo}' no es válido para una clase.")


def _validar_fechas(body, errores):
    inicio = body.get("fecha_hora_inicio")
    fin = body.get("fecha_hora_fin")
    inicio_ok = False
    fin_ok = False

    if inicio:
        try:
            validaciones.validar_fecha_hora(inicio, "fecha_hora_inicio")
            inicio_ok = True
        except ValidationError as e:
            errores.append(str(e))

    if fin:
        try:
            validaciones.validar_fecha_hora(fin, "fecha_hora_fin")
            fin_ok = True
        except ValidationError as e:
            errores.append(str(e))

    if inicio_ok and fin_ok:
        try:
            validaciones.validar_rango_fecha(inicio, fin, "fecha_hora_inicio", "fecha_hora_fin")
        except ValidationError as e:
            errores.append(str(e))


def _validar_status(body, errores):
    if "status" in body and body["status"] is not None:
        try:
            validaciones.validar_valor_en(body["status"], ESTADOS_CLASE, "status")
        except ValidationError as e:
            errores.append(str(e))


def validar_body_crear_clase(body):
    validaciones.validar_body_presente(body)
    body = _strip_strings(body)

    errores = []
    _validar_obligatorios(body, errores)
    _validar_extras(body, errores)
    _validar_fechas(body, errores)
    _validar_status(body, errores)

    if errores:
        raise ValidationError(errores)

    return body


def validar_body_reemplazar_clase(body):
    return validar_body_crear_clase(body)


def validar_body_modificar_clase_parcial(body):
    # PATCH parcial: chequea campos extra y formato individual de los campos enviados.
    # El service debe luego mergear con la clase actual y revalidar con validar_body_reemplazar_clase.
    validaciones.validar_body_presente(body)
    body = _strip_strings(body)

    errores = []
    _validar_extras(body, errores)

    if "fecha_hora_inicio" in body and body["fecha_hora_inicio"]:
        try:
            validaciones.validar_fecha_hora(body["fecha_hora_inicio"], "fecha_hora_inicio")
        except ValidationError as e:
            errores.append(str(e))

    if "fecha_hora_fin" in body and body["fecha_hora_fin"]:
        try:
            validaciones.validar_fecha_hora(body["fecha_hora_fin"], "fecha_hora_fin")
        except ValidationError as e:
            errores.append(str(e))

    _validar_status(body, errores)

    if errores:
        raise ValidationError(errores)

    return body


def validar_filtros_clases(filtros, es_admin):
    errores = []

    extras = set(filtros.keys()) - set(FILTROS_PERMITIDOS)
    for campo in sorted(extras):
        errores.append(
            f"Filtro '{campo}' no permitido. Filtros permitidos: {', '.join(FILTROS_PERMITIDOS)}."
        )

    if "status" in filtros:
        try:
            validaciones.validar_valor_en(filtros["status"], ESTADOS_CLASE, "status")
        except ValidationError as e:
            errores.append(str(e))

    if "fecha" in filtros:
        try:
            validaciones.validar_fecha(filtros["fecha"], "fecha")
        except ValidationError as e:
            errores.append(str(e))

    if "activa" in filtros:
        valor = filtros["activa"]
        if isinstance(valor, str):
            valor_lower = valor.lower()
            if valor_lower == "true":
                filtros["activa"] = True
            elif valor_lower == "false":
                if not es_admin:
                    errores.append("El filtro 'activa=false' solo puede ser utilizado por administradores.")
                else:
                    filtros["activa"] = False
            else:
                errores.append("El filtro 'activa' debe ser un valor booleano (true o false).")

    if errores:
        raise ValidationError(errores)

    return filtros
