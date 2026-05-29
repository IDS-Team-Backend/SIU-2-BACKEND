from flask import request, jsonify, Blueprint
import services.cursos_service as logic
from utils import auth_validator as auth
from config import ADMIN, ALUMNO, DOCENTE
from utils.error_handlers import created_response, ValidationError
from utils import paginacion

cursos_bp = Blueprint("cursos", __name__)


@cursos_bp.get("/me")
@auth.requiere_roles(ALUMNO, DOCENTE)
def get_mis_cursos():
    usuario_id = auth.obtener_usuario_id()

    if auth.usuario_es(DOCENTE):
        rol = DOCENTE
    else:
        rol = ALUMNO

    cursos = logic.obtener_cursos_del_usuario_actual(usuario_id, rol)
    return jsonify({"cursos": cursos, "total": len(cursos)}), 200

@cursos_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"resource": "cursos", "status": "healthy"}), 200

@cursos_bp.route("/", methods=["GET"])
def obtener_cursos():
    page, page_size, offset = paginacion.desde_request()

    materia_id = request.args.get("materia_id", type=int)
    nombre = request.args.get("nombre")
    anio = request.args.get("anio", type=int)
    cuatrimestre = request.args.get("cuatrimestre", type=int)
    profesor_id = request.args.get("profesor_id", type=int)

    cursos, total = logic.obtener_cursos(
        materia_id, nombre, anio, cuatrimestre, profesor_id, page_size, offset
    )

    if not cursos:
        return "", 204

    return jsonify({
        "cursos": cursos,
        "total": total,
        "page": page,
        "page_size": page_size
    }), 200

@cursos_bp.route("/", methods=["POST"])
@auth.requiere_roles(ADMIN)
def crear_cursos():
    parametros = request.get_json(silent=True)

    if parametros is None:
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    new_curso = logic.crear_cursos(parametros)

    return created_response({
        "message": "Curso creado exitosamente",
        "curso": new_curso
    }, f"/cursos/{new_curso['id']}")

@cursos_bp.route("/<int:curso_id>", methods=["GET"])
def obtener_curso(curso_id):
    curso = logic.obtener_curso(curso_id)
    return jsonify(curso), 200

@cursos_bp.route("/<int:curso_id>", methods=["PUT"])
@auth.requiere_roles(ADMIN)
def reemplazar_curso(curso_id):
    parametros = request.get_json(silent=True)

    if parametros is None:
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    updated_curso = logic.reemplazar_curso(curso_id, parametros)

    return jsonify({
        "message": "Curso actualizado exitosamente",
        "curso": updated_curso
    }), 200

@cursos_bp.route("/<int:curso_id>", methods=["DELETE"])
@auth.requiere_roles(ADMIN)
def eliminar_curso(curso_id: int):
    logic.eliminar_curso(curso_id)
    return "", 204

@cursos_bp.route("/<curso_id>", methods=["GET", "PUT", "DELETE"])
def curso_id_invalido(curso_id):
    raise ValidationError("El ID de curso debe ser un número entero positivo.")