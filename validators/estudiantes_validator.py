from utils import validaciones


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
        anio_ingreso = validaciones.validar_minimo(anio_ingreso, 1900, "anio_ingreso")
        anio_ingreso = validaciones.validar_maximo(anio_ingreso, 2100, "anio_ingreso")
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
        anio_ingreso = validaciones.validar_minimo(anio_ingreso, 1900, "anio_ingreso")
        anio_ingreso = validaciones.validar_maximo(anio_ingreso, 2100, "anio_ingreso")
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
