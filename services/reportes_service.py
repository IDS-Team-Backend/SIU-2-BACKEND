import repositories.reportes_repository as db
from utils.pdf_generator import (
    crear_pdf_alumnos,
    crear_pdf_estadisticas,
    crear_pdf_equipos
)
from utils.validaciones import validar_entero, validar_string_no_vacio

def obtener_reporte_alumnos(
    curso_id=None,
    carrera=None,
    anio_ingreso=None,
    nombre_completo=None,
    padron=None,
    evaluacion_id=None,
    condicion=None,
    nota_mayor_a=None,
    exportar_pdf=False,
    page_size=20,
    offset=0
):
    if curso_id:
        validar_entero(curso_id, "curso_id")
    if anio_ingreso:
        validar_entero(anio_ingreso, "anio_ingreso")
    if padron:
        validar_entero(padron, "padron")
    if carrera:
        validar_string_no_vacio(carrera, "carrera")
    if nombre_completo:
        validar_string_no_vacio(nombre_completo, "nombre_completo")
    if evaluacion_id:
        validar_entero(evaluacion_id, "evaluacion_id")
    if condicion:
        validar_string_no_vacio(condicion, "condicion")
        if condicion.lower() not in ["aprobado", "desaprobado"]:
            from utils.error_handlers import ValidationError
            raise ValidationError(
                "El parámetro 'condicion' debe ser 'aprobado' o 'desaprobado'."
            )
    if nota_mayor_a:
        try:
            float(nota_mayor_a)
        except ValueError:
            from utils.error_handlers import ValidationError
            raise ValidationError(
                "El parámetro 'nota_mayor_a' debe ser un número decimal o entero."
            )

    if exportar_pdf:
        alumnos, _ = db.obtener_alumnos_reporte(
            curso_id=curso_id,
            carrera=carrera,
            anio_ingreso=anio_ingreso,
            nombre_completo=nombre_completo,
            padron=padron,
            evaluacion_id=evaluacion_id,
            condicion=condicion,
            nota_mayor_a=nota_mayor_a,
            page_size=100000,
            offset=0
        )

        return crear_pdf_alumnos(alumnos)

    alumnos, total = db.obtener_alumnos_reporte(
        curso_id=curso_id,
        carrera=carrera,
        anio_ingreso=anio_ingreso,
        nombre_completo=nombre_completo,
        padron=padron,
        evaluacion_id=evaluacion_id,
        condicion=condicion,
        nota_mayor_a=nota_mayor_a,
        page_size=page_size,
        offset=offset
    )

    return alumnos, total


def obtener_reporte_estadisticas(curso_id, exportar_pdf=False):
    validar_entero(curso_id, "curso_id")

    promedio_por_evaluacion = db.obtener_promedio_por_evaluacion(curso_id)

    promedio_por_tipo = db.obtener_promedio_por_tipo(curso_id)

    distribucion_notas = db.obtener_distribucion_notas(curso_id)

    estado_cursada = db.obtener_estado_cursada(curso_id)

    asistencia_por_clase = db.obtener_asistencia_por_clase(curso_id)

    resultado = {
        "promedio_por_evaluacion": promedio_por_evaluacion,
        "promedio_por_tipo": promedio_por_tipo,
        "distribucion_notas": distribucion_notas,
        "estado_cursada": estado_cursada,
        "asistencia_por_clase": asistencia_por_clase
    }

    if exportar_pdf:
        return crear_pdf_estadisticas(resultado)

    return resultado


def obtener_reporte_equipos(curso_id, exportar_pdf=False):
    validar_entero(curso_id, "curso_id")
    equipos = db.obtener_equipos_reporte(curso_id)
    if exportar_pdf:
        return crear_pdf_equipos(equipos)
        
    return equipos