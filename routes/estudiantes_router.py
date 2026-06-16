import math

from flask import request, jsonify, Blueprint

import services.estudiantes_service as logic
import services.carga_masiva_alumnos_service as carga_masiva
from constants import ADMIN, ALUMNO, DOCENTE
from utils.error_handlers import created_response, NotFoundError, ValidationError
from utils import auth_validator as auth
from utils import paginacion
from validators import estudiantes_validator


estudiantes_bp = Blueprint("estudiantes", __name__)

FILTROS_PERMITIDOS = ("carrera", "anio_ingreso", "usuario_id", "q", "eliminados")


def _parsear_filtros():
    for key in request.args.keys():
        if key in ("page", "page_size"):
            continue
        if key not in FILTROS_PERMITIDOS:
            raise ValidationError(
                f"Filtro '{key}' no permitido. Permitidos: {', '.join(FILTROS_PERMITIDOS)}."
            )
    return {
        "carrera": request.args.get("carrera"),
        "anio_ingreso": request.args.get("anio_ingreso", type=int),
        "usuario_id": request.args.get("usuario_id", type=int),
        "q": request.args.get("q"),
        "eliminados": request.args.get("eliminados", "false").lower() == "true",
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
@auth.requiere_roles(ADMIN)
def crear_estudiante():
    parametros = estudiantes_validator.validar_body_crear_estudiante(request.get_json())
    nuevo_estudiante = logic.crear_estudiante(parametros)
    return created_response(
        {"message": "Estudiante creado exitosamente", "estudiante": nuevo_estudiante},
        f"/estudiantes/{nuevo_estudiante['id']}"
    )


@estudiantes_bp.route("/me", methods=["GET"])
def obtener_mi_estudiante():
    estudiante = logic.obtener_estudiante_me()
    return jsonify(estudiante), 200


@estudiantes_bp.route("/<int:id>", methods=["GET"])
@auth.requiere_roles(ADMIN, DOCENTE)
def obtener_estudiante_por_id(id):
    estudiante = logic.obtener_estudiante_por_id(id)
    return jsonify(estudiante), 200


@estudiantes_bp.route("/padron/<int:padron>", methods=["GET"])
@auth.requiere_roles(ADMIN, DOCENTE)
def obtener_estudiante_por_padron(padron):
    estudiante = logic.obtener_estudiante_por_padron(padron)
    return jsonify(estudiante), 200


@estudiantes_bp.route("/<int:id>", methods=["PUT"])
@auth.requiere_roles(ADMIN)
def reemplazar_estudiante(id):
    parametros = estudiantes_validator.validar_body_reemplazar_estudiante(request.get_json())
    if not logic.reemplazar_estudiante(id, parametros):
        raise NotFoundError("No se encontró el estudiante")
    return "", 204


@estudiantes_bp.route("/<int:id>", methods=["PATCH"])
@auth.requiere_roles(ADMIN, DOCENTE, ALUMNO)
def modificar_estudiante_parcial(id):
    parametros = estudiantes_validator.validar_body_modificar_estudiante(request.get_json())
    estudiante = logic.modificar_estudiante_parcial(id, parametros)
    return jsonify({
        "message": "Estudiante actualizado exitosamente",
        "estudiante": estudiante,
    }), 200


@estudiantes_bp.route("/<int:id>", methods=["DELETE"])
@auth.requiere_roles(ADMIN)
def eliminar_estudiante(id: int):
    param_hard = request.args.get("hard", "false").lower() == "true"
    logic.eliminar_estudiante(id, hard_delete=param_hard)
    return "", 204


@estudiantes_bp.route("/<int:id>/reactivar", methods=["POST"])
@auth.requiere_roles(ADMIN)
def reactivar_estudiante(id: int):
    logic.reactivar_estudiante(id)
    return "", 204


@estudiantes_bp.route("/eliminar-lote", methods=["POST"])
@auth.requiere_roles(ADMIN)
def eliminar_lote():
    body = request.get_json(silent=True) or {}
    estudiante_ids = body.get("estudiante_ids")

    if not isinstance(estudiante_ids, list) or not estudiante_ids:
        return jsonify({"error": "Se requiere 'estudiante_ids' como lista no vacía."}), 400

    resultado = logic.eliminar_estudiantes_lote(estudiante_ids)
    return jsonify({"mensaje": "Baja masiva finalizada", "resultado": resultado}), 200


@estudiantes_bp.route("/reactivar-lote", methods=["POST"])
@auth.requiere_roles(ADMIN)
def reactivar_lote():
    body = request.get_json(silent=True) or {}
    estudiante_ids = body.get("estudiante_ids")

    if not isinstance(estudiante_ids, list) or not estudiante_ids:
        return jsonify({"error": "Se requiere 'estudiante_ids' como lista no vacía."}), 400

    resultado = logic.reactivar_estudiantes_lote(estudiante_ids)
    return jsonify({"mensaje": "Reactivación masiva finalizada", "resultado": resultado}), 200


@estudiantes_bp.route("/importar-lote", methods=["POST"])
@auth.requiere_roles(ADMIN)
def importar_lote_estudiantes():
    if 'archivo' not in request.files:
        return jsonify({"error": "No se encontró la parte del archivo en la petición con la clave 'archivo'"}), 400

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo"}), 400

    resultado = carga_masiva.importar_estudiantes_por_lote(archivo)
    return jsonify({
        "mensaje": "Procesamiento de lote finalizado",
        "resultado": resultado,
    }), 200


@estudiantes_bp.route("/<id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def estudiante_id_invalido(id):
    raise ValidationError("El ID debe ser un número entero positivo.")
