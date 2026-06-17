from flask import Blueprint, jsonify, request, send_file
import io
import services.reportes_service as logic
from config import ADMIN, DOCENTE, AYUDANTE
from utils import auth_validator as auth, paginacion
import math


reportes_bp = Blueprint("reportes", __name__)

@reportes_bp.route("/alumnos", methods=["GET"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def obtener_reporte_alumnos():
    curso_id = request.args.get("curso_id")
    carrera = request.args.get("carrera")
    anio_ingreso = request.args.get("anio_ingreso")
    nombre_completo = request.args.get("nombre_completo")
    padron = request.args.get("padron")

    evaluacion_id = request.args.get("evaluacion_id")
    condicion = request.args.get("condicion")
    nota_mayor_a = request.args.get("nota_mayor_a")
    
    exportar_pdf = request.args.get("export", "").lower() == "pdf"
    page, page_size, offset = paginacion.desde_request()


    if exportar_pdf:
        pdf = logic.obtener_reporte_alumnos(
            curso_id=curso_id,
            carrera=carrera,
            anio_ingreso=anio_ingreso,
            nombre_completo=nombre_completo,
            padron=padron,
            evaluacion_id=evaluacion_id,
            condicion=condicion,
            nota_mayor_a=nota_mayor_a,
            exportar_pdf=True
        )

        return send_file(
            io.BytesIO(pdf),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="reporte_alumnos_rendimiento.pdf"
        )

    resultado, total = logic.obtener_reporte_alumnos(
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
        
    if not resultado:
        return "", 204
     
    total_paginas = math.ceil(total / page_size) if page_size else 0

    return jsonify({
        "resultados": resultado,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_paginas": total_paginas,
    }), 200


@reportes_bp.route("/estadisticas", methods=["GET"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def obtener_reporte_estadisticas():
    curso_id = request.args.get("curso_id")
    exportar_pdf = request.args.get("export", "").lower() == "pdf"
    resultado = logic.obtener_reporte_estadisticas(curso_id, exportar_pdf)
    if exportar_pdf:
        return send_file(
            io.BytesIO(resultado),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="reporte_estadisticas.pdf"
        )
        
    return jsonify({"resultados": resultado}), 200


@reportes_bp.route("/equipos", methods=["GET"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def obtener_reporte_equipos():
    curso_id = request.args.get("curso_id")
    exportar_pdf = request.args.get("export", "").lower() == "pdf"
    resultado = logic.obtener_reporte_equipos(curso_id, exportar_pdf)
    
    if exportar_pdf:
        return send_file(
            io.BytesIO(resultado),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="reporte_equipos.pdf"
        )
        
    return jsonify({"resultados": resultado}), 200