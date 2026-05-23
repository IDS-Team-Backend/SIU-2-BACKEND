from flask import Blueprint, jsonify, request
from utils import auth_validator as auth
import services.clases_service as logic
from config import ADMIN, DOCENTE, ESTADOS_CLASE


clases_bp = Blueprint("clases", __name__)
clases_bp.before_request(auth.validar_token)

# ─── GET /clases ───────────────────────────────────────────────────────────────
@clases_bp.get("/")
def get_clases():
    # se sacan los filtros que no se enviaron (value = None)
    filtros = {k: v for k, v in request.args.items() if v is not None and v.strip() != ""}

    clases, total = logic.get_clases(filtros)

    return jsonify({"clases": clases, "total": total}), 200

# ─── GET /clases/{id} ──────────────────────────────────────────────────────────
@clases_bp.get("/<int:clase_id>")
def get_clase(clase_id):
    clase = logic.get_clase_by_id(clase_id)

    return jsonify({"clase": clase}), 200

# ─── POST /clases ──────────────────────────────────────────────────────────────
@clases_bp.post("/")
@auth.requiere_roles(ADMIN, DOCENTE)
def crear_clase():
    args = request.get_json()

    new_clase = logic.crear_clase(args)

    return jsonify({"clase": new_clase}), 201

# ─── GET /clases/estados ────────────────────────────────────────────────────────
@clases_bp.get("/estados")
def get_estados_clase():
    # se convierte la lista de ESTADOS_CLASE en una lista de dicts, donde cada dict es un estado
    lista_de_dicts = [
        {"id": i + 1, "nombre": estado} 
        for i, estado in enumerate(ESTADOS_CLASE)
    ]
    
    return jsonify({"estados": lista_de_dicts}), 200

# ─── PUT /clases/{id} ──────────────────────────────────────────────────────────────
@clases_bp.put("/<int:clase_id>")
@auth.requiere_roles(ADMIN, DOCENTE)
def actualizar_clase(clase_id):
    args = request.get_json()

    clase_actualizada = logic.actualizar_clase(clase_id, args)

    return jsonify({"clase": clase_actualizada}), 200

# ─── PATCH /clases/{id} ──────────────────────────────────────────────────────────────
@clases_bp.patch("/<int:clase_id>")
@auth.requiere_roles(ADMIN, DOCENTE)
def actualizar_clase_parcial(clase_id):
    args = request.get_json()

    clase_actualizada = logic.actualizar_clase_parcial(clase_id, args)

    return jsonify({"clase": clase_actualizada}), 200


# ─── DELETE /clases/{id} ──────────────────────────────────────────────────────────────
@clases_bp.delete("/<int:clase_id>")
@auth.requiere_roles(ADMIN, DOCENTE)
def eliminar_clase(clase_id):
    logic.eliminar_clase(clase_id)

    return jsonify({}), 204