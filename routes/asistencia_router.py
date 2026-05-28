from flask import Blueprint, jsonify, request
from config import DOCENTE, AYUDANTE, ALUMNO
from utils.error_handlers import ValidationError
from utils import auth_validator as auth
import services.asistencia_service as logic


asistencia_bp = Blueprint("asistencia", __name__)


@asistencia_bp.post("/clases/<int:clase_id>/generar-qrs")
@auth.requiere_roles(DOCENTE, AYUDANTE)
def generar_qrs(clase_id):
    logic.generar_qrs_de_asistencia(clase_id)
    
    return jsonify({
        "message": "QRs generados correctamente y enviados por mail",
    }), 201


@asistencia_bp.post("/escanear")
@auth.requiere_roles(DOCENTE, AYUDANTE)
def escanear():
    args = request.get_json(silent=True)

    if not isinstance(args, dict):
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    resultado = logic.escanear_qr(args.get("token"))
    return jsonify(resultado), 200


@asistencia_bp.get("/clases/<int:clase_id>")
@auth.requiere_roles(DOCENTE, AYUDANTE)
def listar_asistencias_clase(clase_id):
    resultado = logic.obtener_asistencias_por_clase(clase_id)
    return jsonify(resultado), 200


@asistencia_bp.put("/clases/<int:clase_id>")
@auth.requiere_roles(DOCENTE, AYUDANTE)
def actualizar_asistencias_clase(clase_id):
    args = request.get_json(silent=True)

    if not isinstance(args, dict):
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    logic.actualizar_asistencias_manualmente(clase_id, args.get("asistencias"))
    return "", 204


@asistencia_bp.get("/cursos/<int:curso_id>/me")
@auth.requiere_roles(ALUMNO)
def mis_asistencias(curso_id):
    resultado = logic.obtener_mis_asistencias(curso_id)
    return jsonify(resultado), 200
