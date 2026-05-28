from flask import Flask, request, jsonify, Blueprint
import services.curso_usuarios_service as logic
from config import ADMIN, ALUMNO, AYUDANTE, DOCENTE
from utils.error_handlers import created_response, ValidationError
from utils import auth_validator as auth

curso_usuarios_bp = Blueprint("curso_usuarios", __name__)


@curso_usuarios_bp.route("/", methods=["GET"])
@auth.requiere_roles("ADMIN", "DOCENTE", "AYUDANTE", "ALUMNO")
def obtener_curso_usuarios():
    usuario_id = request.args.get("usuario_id")
    curso_id = request.args.get("curso_id")
    estado = request.args.get("estado")
    
    # Atrapamos los parámetros de paginación 
    page_size = int(request.args.get("page_size", 20))
    offset = int(request.args.get("offset", 0))

   
    registros, total = logic.obtener_curso_usuarios(
        usuario_id, curso_id, estado, page_size, offset
    )

    if not registros:
        return "", 204

    return jsonify({"curso_usuarios": registros, "total": total}), 200


@curso_usuarios_bp.route("/", methods=["POST"])
@auth.requiere_roles("ADMIN", "DOCENTE")
def crear_curso_usuario():
    data = request.get_json()
    registro = logic.crear_curso_usuario(data)
    return jsonify(registro), 201



@curso_usuarios_bp.route("/<int:id>", methods=["PUT"])
@auth.requiere_roles("ADMIN", "DOCENTE")
def reemplazar_curso_usuario(curso_id):
    data = request.get_json(silent=True)

    if data is None:
        raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

    updated_curso_estudiante = logic.reemplazar_curso_usuario(curso_id, data)

    return jsonify({
        "message": "Curso actualizado exitosamente",
        "curso": updated_curso_estudiante
    }), 200



@curso_usuarios_bp.route("/<int:id>", methods=["DELETE"])
@auth.requiere_roles("admin", "DOCENTE")
def eliminar_curso_usuario(id):
    logic.eliminar_curso_usuario(id)
    
    return "", 204

@curso_usuarios_bp.route("/importar-lote", methods=["POST"])
@auth.requiere_roles(ADMIN, DOCENTE)
def importar_lote_estudiantes():
    if 'archivo' not in request.files:
        return jsonify({"error": "No se encontró la parte del archivo en la petición con la clave 'archivo'"}), 400
        
    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo"}), 400

    resultado_proceso = logic.importar_inscripciones_por_lote(archivo)
    return jsonify({
        "mensaje": "Procesamiento de lote finalizado",
        "resultado": resultado_proceso
    }), 200