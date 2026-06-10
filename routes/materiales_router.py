from flask import Blueprint, jsonify, request
import services.materiales_service as logic
from config import ADMIN, DOCENTE, AYUDANTE, ALUMNO
from utils import auth_validator as auth


materiales_bp = Blueprint("materiales", __name__)

# Solo protege las rutas que modifican datos
@materiales_bp.before_request
def proteger_rutas_modificacion():
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        auth.validar_token()

@materiales_bp.route("/", methods=["GET"])

def obtener_materiales():
    curso_id   = request.args.get("curso_id")
    subido_por = request.args.get("subido_por")
 
    page_size = int(request.args.get("page_size", 20))
    offset    = int(request.args.get("offset", 0))
 
    registros, total = logic.obtener_materiales(curso_id, subido_por, page_size, offset)
 
    if not registros:
        return "", 204
 
    return jsonify({"materiales": registros, "total": total}), 200
 
 
@materiales_bp.route("/<int:id>", methods=["GET"])

def obtener_material(id):
    material = logic.obtener_material_por_id(id)
    return jsonify(material), 200
 
 
@materiales_bp.route("/", methods=["POST"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def crear_material():
    data = request.get_json()
    material = logic.crear_material(data)
    return jsonify({"message": "Material creado exitosamente", "material": material}), 201
 
 
@materiales_bp.route("/<int:id>", methods=["PUT"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def reemplazar_material(id):
    data = request.get_json()
    logic.reemplazar_material(id, data)
    return "", 204
 
 
@materiales_bp.route("/<int:id>", methods=["PATCH"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def actualizar_material(id):
    data = request.get_json()
    logic.actualizar_material(id, data)
    return "", 204
 
 
@materiales_bp.route("/<int:id>", methods=["DELETE"])
@auth.requiere_roles(ADMIN, DOCENTE)
def eliminar_material(id):
    param_hard = request.args.get("hard", "false").lower() == "true"
    logic.eliminar_material(id, hard_delete=param_hard)
    return "", 204
 