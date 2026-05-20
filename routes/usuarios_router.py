from flask import Flask, request, jsonify, Blueprint
import services.usuarios_service as logic
from utils.error_handlers import created_response, ValidationError

usuarios_bp = Blueprint("usuarios", __name__)

usuario_params = ["nombre", "apellido", "dni", "email", "rol_id"]

@usuarios_bp.get("/health")
def health_check():
    return jsonify({"resource": "usuarios", "status": "ok"})


@usuarios_bp.route("/", methods=["GET"])
def obtener_usuarios():
    nombre = request.args.get("nombre")
    apellido = request.args.get("apellido")
    dni = request.args.get("dni")
    email = request.args.get("email")
    rol_id = request.args.get("rol_id")

    usuarios, total = logic.obtener_usuarios(nombre, apellido, email, dni, rol_id)

    if not usuarios:
        return "", 204

    return jsonify({"usuarios": usuarios, "total": total}), 200


# ─── POST /usuarios ───────────────────────────────────────────────────────────

@usuarios_bp.route("/", methods=["POST"])
def crear_usuario():
    parametros = request.get_json()
    new_usuario = logic.crear_usuario(parametros)
    return created_response({"message": "Usuario creado exitosamente", "usuario": new_usuario}, f"/usuarios/{new_usuario['id']}")


# ─── GET /usuarios/{id} ───────────────────────────────────────────────────────

@usuarios_bp.route("/<int:id>", methods=["GET"])
def obtener_usuario_por_id(id):
    usuario = logic.obtener_usuario_por_id(id)
    return jsonify(usuario), 200


# ─── PUT /usuarios/{id} ───────────────────────────────────────────────────────

@usuarios_bp.route("/<int:id>", methods=["PUT"])
def reemplazar_usuario(id):
    parametros = request.get_json()
    actualizado = logic.reemplazar_usuario(id, parametros)
    if not actualizado:
        return {"error": "Usuario no encontrado"}, 404
    return "", 204

# ─── DELETE /usuarios/{id} ────────────────────────────────────────────────────
@usuarios_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_usuario(id: int):
    logic.eliminar_usuario(id)
    return "", 204


# ─── Catch-all para IDs no numéricos ─────────────────────────────────────────

@usuarios_bp.route("/<id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def usuario_id_invalido(id):
    raise ValidationError("El ID debe ser un número entero positivo.")