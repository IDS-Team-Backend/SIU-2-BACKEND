import math

from flask import request, jsonify, Blueprint

import services.estudiante_curso_service as logic
from constants import ADMIN, ALUMNO, AYUDANTE, DOCENTE
from utils.error_handlers import created_response, NotFoundError, ValidationError
from utils import auth_validator as auth
from utils import paginacion
from validators import estudiante_curso_validator
import services.carga_masiva_alumnos_service as carga_masiva


estudiante_curso_bp = Blueprint("estudiante_curso", __name__)

FILTROS_PERMITIDOS = ("estudiante_id", "curso_id", "estado", "q")


def _parsear_filtros():
    for key in request.args.keys():
        if key in ("page", "page_size"):
            continue
        if key not in FILTROS_PERMITIDOS:
            raise ValidationError(
                f"Filtro '{key}' no permitido. Permitidos: {', '.join(FILTROS_PERMITIDOS)}."
            )

    return {
        "estudiante_id": request.args.get("estudiante_id", type=int),
        "curso_id": request.args.get("curso_id", type=int),
        "estado": request.args.get("estado"),
        "q": request.args.get("q"),
    }


@estudiante_curso_bp.route("/", methods=["GET"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE, ALUMNO)
def obtener_estudiante_cursos():
    filtros = _parsear_filtros()
    page, page_size, offset = paginacion.desde_request()

    estudiante_cursos, total = logic.obtener_estudiante_cursos(
        **filtros,
        page_size=page_size,
        offset=offset,
    )

    if not estudiante_cursos:
        return "", 204

    total_paginas = math.ceil(total / page_size) if page_size else 0
    return jsonify({
        "estudiante_cursos": estudiante_cursos,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_paginas": total_paginas,
    }), 200


@estudiante_curso_bp.route("/", methods=["POST"])
@auth.requiere_roles(ADMIN, DOCENTE)
def crear_estudiante_curso():
    parametros = estudiante_curso_validator.validar_body_crear_estudiante_curso(request.get_json())
    nueva_inscripcion = logic.crear_estudiante_curso(parametros)
    return created_response(
        {"message": "Inscripción creada exitosamente", "estudiante_curso": nueva_inscripcion},
        f"/estudiante_curso/{nueva_inscripcion['id']}"
    )


@estudiante_curso_bp.route("/importar-lote", methods=["POST"])
@auth.requiere_roles(ADMIN, DOCENTE)
def importar_lote_estudiante_curso():
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


@estudiante_curso_bp.route("/<int:id>", methods=["GET"])
@auth.requiere_roles(ADMIN, DOCENTE, AYUDANTE)
def obtener_estudiante_curso_por_id(id):
    estudiante_curso = logic.obtener_estudiante_curso_por_id(id)
    return jsonify(estudiante_curso), 200


@estudiante_curso_bp.route("/<int:id>", methods=["PUT"])
@auth.requiere_roles(ADMIN, DOCENTE)
def reemplazar_estudiante_curso(id):
    parametros = estudiante_curso_validator.validar_body_reemplazar_estudiante_curso(request.get_json())
    if not logic.reemplazar_estudiante_curso(id, parametros):
        raise NotFoundError("No se encontró la inscripción.")
    return "", 204


@estudiante_curso_bp.route("/<int:id>", methods=["PATCH"])
@auth.requiere_roles(ADMIN, DOCENTE)
def modificar_estudiante_curso_parcial(id):
    parametros = estudiante_curso_validator.validar_body_modificar_estudiante_curso(request.get_json())
    estudiante_curso = logic.modificar_estudiante_curso_parcial(id, parametros)
    return jsonify({
        "message": "Inscripción actualizada exitosamente",
        "estudiante_curso": estudiante_curso,
    }), 200


@estudiante_curso_bp.route("/<int:id>", methods=["DELETE"])
@auth.requiere_roles(ADMIN, DOCENTE)
def eliminar_estudiante_curso(id):
    logic.eliminar_estudiante_curso(id)
    return "", 204


@estudiante_curso_bp.route("/<id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def estudiante_curso_id_invalido(id):
    raise ValidationError("El ID debe ser un número entero positivo.")


@estudiante_curso_bp.route("/inscribir-lote", methods=["POST"])
@auth.requiere_roles(ADMIN, DOCENTE)
def inscribir_lote_por_ids():
    body = request.get_json(silent=True) or {}
    curso_id = body.get("curso_id")
    estudiante_ids = body.get("estudiante_ids")
    estado = body.get("estado", "activo")

    if curso_id is None:
        return jsonify({"error": "falta el curso_id"}), 400
    if not isinstance(estudiante_ids, list) or not estudiante_ids:
        return jsonify({"error": "Se requiere 'estudiante_ids' como lista no vacía."}), 400

    try:
        curso_id = int(curso_id)
    except (ValueError, TypeError):
        return jsonify({"error": "'curso_id' debe ser un entero."}), 400

    resultado = carga_masiva.inscribir_lote_por_ids(curso_id, estudiante_ids, estado)
    return jsonify({
        "mensaje": "Inscripción masiva finalizada",
        "resultado": resultado,
    }), 200

@estudiante_curso_bp.route("/desvincular-lote", methods=["POST"])
@auth.requiere_roles(ADMIN, DOCENTE)
def desvincular_lote():
    body = request.get_json(silent=True) or {}
    curso_id = body.get("curso_id")
    estudiante_ids = body.get("estudiante_ids")

    if curso_id is None:
        return jsonify({"error": "falta el curso_id"}), 400
    if not isinstance(estudiante_ids, list) or not estudiante_ids:
        return jsonify({"error": "Se requiere 'estudiante_ids' como lista."}), 400

    resultado = carga_masiva.desvincular_lote_por_ids(int(curso_id), estudiante_ids)
    return jsonify({"mensaje": "Desvinculación masiva finalizada", "resultado": resultado}), 200