from flask import request, jsonify, Blueprint
import services.cursos_service as logic
from utils import auth_validator as auth
from utils.error_handlers import created_response, ValidationError


cursos_bp = Blueprint('cursos', __name__)
cursos_bp.before_request(auth.validar_token)

cursos_params = ['materia_id', 'nombre', 'anio', 'cuatrimestre',]

@cursos_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"resource": "cursos", "status": "healthy"}), 200

@cursos_bp.route('/', methods=['GET'])
def obtener_cursos():
    materia = request.args.get('materia_id')
    nombre = request.args.get('nombre')
    anio = request.args.get('anio')
    cuatrimestre = request.args.get('cuatrimestre')

    cursos, total = logic.obtener_cursos(materia, nombre, anio, cuatrimestre)

    if not cursos:
        return "", 204
    
    return jsonify({"cursos": cursos, "total": total}), 200

#---------POST / cursos--------------

@cursos_bp.route('/', methods=['POST'])
def crear_cursos():
    parametros = request.get_json()
    new_curso = logic.crear_cursos(parametros)
    return created_response({
        "message": "Curso creado exitosamente",
        "curso": new_curso},
        f"/cursos/{new_curso['id']}")


#---------GET / cursos/{id}--------------
@cursos_bp.route('/<int:curso_id>', methods=['GET'])
def obtener_curso(curso_id):
    curso = logic.obtener_curso(curso_id)
    return jsonify(curso), 200

#--------- PUT / cursos/{id} --------------
@cursos_bp.route('/<int:curso_id>', methods=['PUT'])
def remplazar_curso(curso_id):
    parametros = request.get_json()
    updated_curso = logic.remplazar_curso(curso_id, parametros)
    
    if not updated_curso:
        return jsonify({"error": "Curso no encontrado"}), 404
    return jsonify({
        "message": "Curso actualizado exitosamente",
        "curso": updated_curso}), 200

#--------- DELETE / cursos/{id} --------------
@cursos_bp.route("/<int:curso_id>", methods=["DELETE"])
def eliminar_curso(curso_id: int):
    logic.eliminar_curso(curso_id)
    return "", 204

#------ Catch all para ids no numericos --------
@cursos_bp.route('/<curso_id>', methods=['GET', 'PUT', 'DELETE'])
def curso_id_invalido(curso_id):
    return jsonify({"error": "ID de curso inválido. Debe ser un número entero."}), 400

    

    