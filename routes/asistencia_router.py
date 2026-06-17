from flask import Blueprint, jsonify, request
from constants import ADMIN, DOCENTE, AYUDANTE, ALUMNO
from utils.error_handlers import ValidationError
from utils import auth_validator as auth
import services.asistencia_service as logic


asistencia_bp = Blueprint("asistencia", __name__)


@asistencia_bp.post("/escanear")
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def escanear():
    args = request.get_json(silent=True)

    if not isinstance(args, dict):
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    resultado = logic.escanear_qr(
        token=args.get("token"),
        clase_id=args.get("clase_id"),
    )
    return jsonify(resultado), 200


@asistencia_bp.get("/clases/<int:clase_id>")
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def listar_asistencias_clase(clase_id):
    resultado = logic.obtener_asistencias_por_clase(clase_id)
    return jsonify(resultado), 200


@asistencia_bp.put("/clases/<int:clase_id>")
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
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
    

@asistencia_bp.get("/cursos/<int:curso_id>/mi-qr")
@auth.requiere_roles(ALUMNO)
def mi_qr(curso_id):
    resultado = logic.obtener_mi_qr(curso_id)
    return jsonify(resultado), 200

@asistencia_bp.get("/cursos/<int:curso_id>/alumnos/<int:alumno_id>")
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def asistencias_de_alumno(curso_id, alumno_id):
    resultado = logic.obtener_asistencias_de_alumno_en_curso(curso_id, alumno_id)
    return jsonify(resultado), 200