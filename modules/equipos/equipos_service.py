from . import equipos_repository as db
from modules.evaluaciones import evaluaciones_repository as evaluaciones_db
from modules.equipo_integrantes import equipo_integrantes_repository as integrantes_db
from modules.estudiantes import estudiantes_repository as estudiantes_db
from utils.csv_handler import leer_csv, procesar_lote
from utils.error_handlers import (
    NotFoundError,
    ValidationError
)
from utils.validaciones import (
    validar_body_presente,
    validar_entero,
    validar_string_no_vacio
)

equipo_params = [
    "curso_id",
    "evaluacion_id",
    "nombre"
]

def obtener_equipos(
    curso_id=None,
    evaluacion_id=None,
    nombre=None
):
    return db.obtener_equipos(
        curso_id,
        evaluacion_id,
        nombre
    )

def crear_equipo(parametros):
    validar_body_presente(parametros)
    for campo in equipo_params:
        if campo not in parametros:
            raise ValidationError(
                f"El campo '{campo}' es requerido."
            )
    curso_id = validar_entero(
        parametros["curso_id"],
        "curso_id"
    )
    evaluacion_id = validar_entero(
        parametros["evaluacion_id"],
        "evaluacion_id"
    )
    nombre = validar_string_no_vacio(
        parametros["nombre"],
        "nombre"
    )
    evaluacion = evaluaciones_db.obtener_evaluacion_por_id(
        evaluacion_id
    )
    if not evaluacion:
        raise NotFoundError(
            "No se encontró la evaluación"
        )
    if not evaluacion["es_grupal"]:
        raise ValidationError(
            "La evaluación no permite equipos."
        )
    return db.crear_equipo(
        curso_id,
        evaluacion_id,
        nombre
    )

def obtener_equipo_por_id(id):
    equipo = db.obtener_equipo_por_id(id)
    if not equipo:
        raise NotFoundError(
            "No se encontró el equipo"
        )

    return equipo

def reemplazar_equipo(id, parametros):
    validar_body_presente(parametros)
    for campo in equipo_params:
        if campo not in parametros:
            raise ValidationError(
                f"El campo '{campo}' es requerido."
            )
    curso_id = validar_entero(
        parametros["curso_id"],
        "curso_id"
    )
    evaluacion_id = validar_entero(
        parametros["evaluacion_id"],
        "evaluacion_id"
    )
    nombre = validar_string_no_vacio(
        parametros["nombre"],
        "nombre"
    )
    evaluacion = evaluaciones_db.obtener_evaluacion_por_id(
        evaluacion_id
    )
    if not evaluacion:
        raise NotFoundError(
            "No se encontró la evaluación"
        )
    if not evaluacion["es_grupal"]:
        raise ValidationError(
            "La evaluación no permite equipos."
        )
    actualizado = db.reemplazar_equipo(
        id,
        curso_id,
        evaluacion_id,
        nombre
    )
    if not actualizado:
        raise NotFoundError(
            "No se encontró el equipo"
        )

    return actualizado

def eliminar_equipo(id, hard_delete=False):
    eliminado = db.eliminar_equipo(id, hard=hard_delete)
    if not eliminado:
        raise NotFoundError("No se encontró el equipo")
    return


def _parsear_padrones(valor):
    """'100001;100002 ;100001' -> [100001, 100002]: enteros, sin vacíos ni duplicados,
    preservando el orden. Lanza ValueError si algún padrón no es numérico."""
    padrones = []
    vistos = set()
    for parte in (valor or "").split(";"):
        parte = parte.strip()
        if not parte:
            continue
        try:
            padron = int(parte)
        except (ValueError, TypeError):
            raise ValueError(f"El padrón '{parte}' no es un número válido.")
        if padron not in vistos:
            vistos.add(padron)
            padrones.append(padron)
    return padrones


def importar_equipos_por_lote(archivo_file, curso_id, evaluacion_id):
    """Carga masiva de equipos para una evaluación grupal a partir de un CSV.

    Cabecera: 'nombre,integrantes' ('integrantes' = padrones separados por ';',
    opcional). curso_id y evaluacion_id vienen del contexto (la URL), no del CSV.

    Política por fila (atómica): nombre ya existente -> duplicado (se ignora);
    padrón inexistente/ inválido -> la fila falla y el equipo no se crea.

    Sin N+1: precarga en lote los nombres de equipos existentes y todos los padrones
    del archivo (una query cada uno) y resuelve cada fila contra esos mapas en memoria;
    los integrantes de un equipo se insertan con un solo executemany.
    """
    curso_id = validar_entero(curso_id, "curso_id")
    evaluacion_id = validar_entero(evaluacion_id, "evaluacion_id")

    evaluacion = evaluaciones_db.obtener_evaluacion_por_id(evaluacion_id)
    if not evaluacion:
        raise NotFoundError("No se encontró la evaluación")
    if not evaluacion["es_grupal"]:
        raise ValidationError("La evaluación no permite equipos.")

    filas = leer_csv(archivo_file, columnas_requeridas={"nombre"})

    # ── Precargas en lote (una query cada una) ────────────────────────────────
    # Nombres ya existentes (case-insensitive, como compara MySQL).
    nombres_existentes = {
        nombre.strip().lower()
        for nombre in db.obtener_nombres_equipos(evaluacion_id)
    }
    # Todos los padrones del archivo -> mapa padron->alumno_id. Los padrones no
    # numéricos se ignoran acá (se reportan luego, por fila).
    todos_padrones = set()
    for fila in filas:
        try:
            todos_padrones.update(_parsear_padrones(fila.get("integrantes", "")))
        except ValueError:
            pass
    mapa_padron_id = {
        est["padron"]: est["id"]
        for est in estudiantes_db.obtener_estudiantes_por_padrones(list(todos_padrones))
    }

    def procesar_fila(fila):
        nombre = (fila.get("nombre") or "").strip()
        if not nombre:
            raise ValueError("El nombre del equipo está vacío.")
        if nombre.lower() in nombres_existentes:
            return "duplicado"

        # Resolver integrantes ANTES de crear el equipo: si un padrón falla, la fila
        # entera falla y no queda un equipo a medias.
        alumno_ids = []
        for padron in _parsear_padrones(fila.get("integrantes", "")):
            alumno_id = mapa_padron_id.get(padron)
            if alumno_id is None:
                raise ValueError(
                    f"No se encontró un estudiante activo con el padrón {padron}."
                )
            alumno_ids.append(alumno_id)

        equipo = db.crear_equipo(curso_id, evaluacion_id, nombre)
        integrantes_db.agregar_integrantes(equipo["id"], alumno_ids)

        # Mantener el set al día para detectar nombres repetidos dentro del mismo CSV.
        nombres_existentes.add(nombre.lower())
        return "creado"

    return procesar_lote(filas, procesar_fila)
