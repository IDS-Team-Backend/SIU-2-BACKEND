import math

from flask import request, jsonify, Blueprint

import services.estudiantes_service as logic
from utils.error_handlers import created_response, NotFoundError, ValidationError
from utils import auth_validator as auth
from utils import paginacion
from validators import estudiantes_validator


estudiantes_bp = Blueprint("estudiantes", __name__)
estudiantes_bp.before_request(auth.validar_token)


def _parsear_filtros():
    activo_arg = request.args.get("activo")
    activo = activo_arg.lower() in ("true", "1") if activo_arg is not None else None

    return {
        "carrera": request.args.get("carrera"),
        "anio_ingreso": request.args.get("anio_ingreso", type=int),
        "activo": activo,
        "usuario_id": request.args.get("usuario_id", type=int),
    }


@estudiantes_bp.route("/", methods=["GET"])
def obtener_estudiantes():
    filtros = _parsear_filtros()
    page, page_size, offset = paginacion.desde_request()

    estudiantes, total = logic.obtener_estudiantes(
        **filtros,
        page_size=page_size,
        offset=offset,
    )

    if not estudiantes:
        return "", 204

    total_paginas = math.ceil(total / page_size) if page_size else 0
    return jsonify({
        "estudiantes": estudiantes,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_paginas": total_paginas,
    }), 200


@estudiantes_bp.route("/", methods=["POST"])
@auth.requiere_roles("admin")
def crear_estudiante():
    parametros = estudiantes_validator.validar_body_crear_estudiante(request.get_json())
    nuevo_estudiante = logic.crear_estudiante(parametros)
    return created_response(
        {"message": "Estudiante creado exitosamente", "estudiante": nuevo_estudiante},
        f"/estudiantes/{nuevo_estudiante['id']}"
    )


@estudiantes_bp.route("/<int:id>", methods=["GET"])
@auth.requiere_roles("admin", "profesor")
def obtener_estudiante_por_id(id):
    estudiante = logic.obtener_estudiante_por_id(id)
    return jsonify(estudiante), 200


@estudiantes_bp.route("/<int:id>", methods=["PUT"])
@auth.requiere_roles("admin")
def reemplazar_estudiante(id):
    parametros = estudiantes_validator.validar_body_reemplazar_estudiante(request.get_json())
    if not logic.reemplazar_estudiante(id, parametros):
        raise NotFoundError("No se encontró el estudiante")
    return "", 204


@estudiantes_bp.route("/<int:id>", methods=["DELETE"])
@auth.requiere_roles("admin")
def eliminar_estudiante(id: int):
    logic.eliminar_estudiante(id)
    return "", 204


@estudiantes_bp.route("/<id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def estudiante_id_invalido(id):
    raise ValidationError("El ID debe ser un número entero positivo.")
