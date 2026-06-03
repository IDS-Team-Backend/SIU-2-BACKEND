from flask import Blueprint, jsonify, request, send_file
import io
import services.reportes_service as logic
from config import ADMIN, DOCENTE, AYUDANTE
from utils import auth_validator as auth

reportes_bp = Blueprint("reportes", __name__)
reportes_bp.before_request(auth.validar_token)

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

    resultado = logic.obtener_reporte_alumnos(
        curso_id=curso_id,
        carrera=carrera,
        anio_ingreso=anio_ingreso,
        nombre_completo=nombre_completo,
        padron=padron,
        evaluacion_id=evaluacion_id,
        condicion=condicion,
        nota_mayor_a=nota_mayor_a,
        exportar_pdf=exportar_pdf
    )
    
    if exportar_pdf:
        return send_file(
            io.BytesIO(resultado),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="reporte_alumnos_rendimiento.pdf"
        )
        
    return jsonify({"resultados": resultado}), 200


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