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
    exportar_pdf=False
):
    if curso_id: validar_entero(curso_id, "curso_id")
    if anio_ingreso: validar_entero(anio_ingreso, "anio_ingreso")
    if padron: validar_entero(padron, "padron")
    if carrera: validar_string_no_vacio(carrera, "carrera")
    if nombre_completo: validar_string_no_vacio(nombre_completo, "nombre_completo")
        
    if evaluacion_id:
        validar_entero(evaluacion_id, "evaluacion_id")
    if condicion:
        validar_string_no_vacio(condicion, "condicion")
        if condicion.lower() not in ["aprobado", "desaprobado"]:
            from utils.error_handlers import ValidationError
            raise ValidationError("El parámetro 'condicion' debe ser 'aprobado' o 'desaprobado'.")
    if nota_mayor_a:
        try:
            float(nota_mayor_a)
        except ValueError:
            from utils.error_handlers import ValidationError
            raise ValidationError("El parámetro 'nota_mayor_a' debe ser un número decimal o entero.")

    alumnos = db.obtener_alumnos_reporte(
        curso_id=curso_id, 
        carrera=carrera, 
        anio_ingreso=anio_ingreso, 
        nombre_completo=nombre_completo, 
        padron=padron,
        evaluacion_id=evaluacion_id,
        condicion=condicion,
        nota_mayor_a=nota_mayor_a
    )
    
    if exportar_pdf:
        return crear_pdf_alumnos(alumnos)
        
    return alumnos


def obtener_reporte_estadisticas(curso_id, exportar_pdf=False):
    validar_entero(curso_id, "curso_id")
    
    stats = db.obtener_estadisticas_aprobacion(curso_id)
    
    for row in stats:
        row['total_notas'] = int(row['total_notas']) if row['total_notas'] else 0
        row['aprobados'] = int(row['aprobados']) if row['aprobados'] else 0
        row['desaprobados'] = int(row['desaprobados']) if row['desaprobados'] else 0
        row['nota_promedio'] = float(row['nota_promedio']) if row['nota_promedio'] else 0.0
        
    if exportar_pdf:
        return crear_pdf_estadisticas(stats)
        
    return stats


def obtener_reporte_equipos(curso_id, exportar_pdf=False):
    validar_entero(curso_id, "curso_id")
    equipos = db.obtener_equipos_reporte(curso_id)
    if exportar_pdf:
        return crear_pdf_equipos(equipos)
        
    return equipos