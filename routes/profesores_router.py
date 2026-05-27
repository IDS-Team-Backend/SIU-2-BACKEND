import math

from flask import request, jsonify, Blueprint

import services.profesores_service as logic
from config import ADMIN, DOCENTE
from utils.error_handlers import created_response, NotFoundError, ValidationError
from utils import auth_validator as auth
from utils import paginacion
from validators import profesores_validator


profesores_bp = Blueprint("profesores", __name__)

FILTROS_PERMITIDOS = ("departamento", "titulo", "activo", "usuario_id")


def _parsear_filtros():
    for key in request.args.keys():
        if key in ("page", "page_size"):
            continue
        if key not in FILTROS_PERMITIDOS:
            raise ValidationError(
                f"Filtro '{key}' no permitido. Permitidos: {', '.join(FILTROS_PERMITIDOS)}."
            )

    activo_arg = request.args.get("activo")
    activo = activo_arg.lower() in ("true", "1") if activo_arg is not None else None

    return {
        "departamento": request.args.get("departamento"),
        "titulo": request.args.get("titulo"),
        "activo": activo,
        "usuario_id": request.args.get("usuario_id", type=int),
    }


@profesores_bp.route("/", methods=["GET"])
def obtener_profesores():
    filtros = _parsear_filtros()
    page, page_size, offset = paginacion.desde_request()

    profesores, total = logic.obtener_profesores(
        **filtros,
        page_size=page_size,
        offset=offset,
    )

    if not profesores:
        return "", 204

    total_paginas = math.ceil(total / page_size) if page_size else 0
    return jsonify({
        "profesores": profesores,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_paginas": total_paginas,
    }), 200


@profesores_bp.route("/", methods=["POST"])
@auth.requiere_roles(ADMIN)
def crear_profesor():
    parametros = profesores_validator.validar_body_crear_profesor(request.get_json())
    nuevo_profesor = logic.crear_profesor(parametros)
    return created_response(
        {"message": "Profesor creado exitosamente", "profesor": nuevo_profesor},
        f"/profesores/{nuevo_profesor['id']}"
    )


@profesores_bp.route("/me", methods=["GET"])
def obtener_mi_profesor():
    profesor = logic.obtener_profesor_me()
    return jsonify(profesor), 200


@profesores_bp.route("/<int:id>", methods=["GET"])
@auth.requiere_roles(ADMIN, DOCENTE)
def obtener_profesor_por_id(id):
    profesor = logic.obtener_profesor_por_id(id)
    return jsonify(profesor), 200


@profesores_bp.route("/<int:id>", methods=["PUT"])
@auth.requiere_roles(ADMIN)
def reemplazar_profesor(id):
    parametros = profesores_validator.validar_body_reemplazar_profesor(request.get_json())
    if not logic.reemplazar_profesor(id, parametros):
        raise NotFoundError("No se encontró el profesor")
    return "", 204


@profesores_bp.route("/<int:id>", methods=["PATCH"])
@auth.requiere_roles(ADMIN, DOCENTE)
def modificar_profesor_parcial(id):
    parametros = profesores_validator.validar_body_modificar_profesor(request.get_json())
    profesor = logic.modificar_profesor_parcial(id, parametros)
    return jsonify({
        "message": "Profesor actualizado exitosamente",
        "profesor": profesor,
    }), 200


@profesores_bp.route("/<int:id>", methods=["DELETE"])
@auth.requiere_roles(ADMIN)
def eliminar_profesor(id: int):
    logic.eliminar_profesor(id)
    return "", 204


@profesores_bp.route("/<id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def profesor_id_invalido(id):
    raise ValidationError("El ID debe ser un número entero positivo.")
