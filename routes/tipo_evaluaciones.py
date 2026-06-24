from flask import Blueprint, jsonify, request

from config import ADMIN, DOCENTE, ROLES_STAFF
from utils import auth_validator as auth

from services.tipos_evaluacion_service import (
    listar_tipos_evaluacion,
    crear_nuevo_tipo_evaluacion,
    actualizar_tipo_evaluacion_service,
    eliminar_tipo_evaluacion_service,
)

tipos_evaluacion_bp = Blueprint("tipos_evaluacion",__name__)

@tipos_evaluacion_bp.route("/",methods=["GET"])
def listar():
    tipos = listar_tipos_evaluacion()
    return jsonify({
        "tipos_evaluacion": tipos
    }), 200


@tipos_evaluacion_bp.route("/",methods=["POST"])
@auth.requiere_roles(*ROLES_STAFF)
def crear():
    data = request.get_json()
    nuevo_id = crear_nuevo_tipo_evaluacion(
        nombre=data.get("nombre"),
        es_grupal=data.get("es_grupal", False)
    )

    return jsonify({
        "mensaje": "Tipo de evaluación creado correctamente.",
        "id": nuevo_id
    }), 201


@tipos_evaluacion_bp.route("/<int:tipo_evaluacion_id>",methods=["PUT"])
@auth.requiere_roles(*ROLES_STAFF)
def actualizar(tipo_evaluacion_id):
    data = request.get_json()
    actualizar_tipo_evaluacion_service(
        tipo_evaluacion_id=tipo_evaluacion_id,
        nombre=data.get("nombre"),
        es_grupal=data.get("es_grupal", False)
    )
    return jsonify({
        "mensaje": "Tipo de evaluación actualizada correctamente."
    }), 200



@tipos_evaluacion_bp.route("/<int:tipo_evaluacion_id>",methods=["DELETE"])
@auth.requiere_roles(*ROLES_STAFF)
def eliminar(tipo_evaluacion_id):
    eliminar_tipo_evaluacion_service(
        tipo_evaluacion_id
    )

    return jsonify({
        "mensaje": "Tipo de evaluación eliminado correctamente."
    }), 200


