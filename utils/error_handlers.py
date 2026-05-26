from flask import jsonify
from werkzeug.exceptions import BadRequest


def created_response(body, resource_path):
    response = jsonify(body)
    response.headers["Location"] = resource_path
    return response, 201

class NotFoundError(Exception): pass
class ValidationError(Exception): pass
class DuplicateError(Exception): pass
class UnauthorizedError(Exception): pass
class ForbiddenError(Exception): pass


def start(app):

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(e):
        return jsonify({
            "errors": [
                {
                    "code": "NOT_FOUND",
                    "message": str(e),
                    "level": "error",
                }
            ]
        }), 404
    
    @app.errorhandler(BadRequest)
    def handle_bad_request_error(e):
        return jsonify({
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "description": f"El JSON enviado está mal formado. Detalles: {e.description}",
                    "message": "Sintaxis JSON inválida"
                }
            ]
        }), 400
    
    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized_error(e):
        return jsonify({
            "errors": [
                {
                    "code": "UNAUTHORIZED",
                    "message": str(e),
                    "level": "error",
                }
            ]
        }), 401
    
    @app.errorhandler(ForbiddenError)
    def handle_forbidden_error(e):
        return jsonify({
            "errors": [
                {
                    "code": "FORBIDDEN",
                    "message": str(e),
                    "level": "error",
                }
            ]
        }), 403

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        # acepta raise ValidationError("msg") o raise ValidationError(["msg1", "msg2"])
        raw = e.args[0] if e.args else ""
        mensajes = raw if isinstance(raw, list) else [raw]
        return jsonify({
            "errors": [
                {"code": "BAD_REQUEST", "message": m, "level": "error"}
                for m in mensajes
            ]
        }), 400

    @app.errorhandler(DuplicateError)
    def handle_duplicate_error(e):
        return jsonify({
            "errors": [
                {
                    "code": "CONFLICT",
                    "message": str(e),
                    "level": "error",
                }
            ]
        }), 409

    @app.errorhandler(ValueError)
    def handle_value_error(e):
        # los validators tiran ValueError(construir_error_api(...)) → e.args[0] = {"errors": [...]}
        raw = e.args[0] if e.args else None
        if isinstance(raw, dict) and "errors" in raw:
            return jsonify(raw), 400
        # ValueError común sin estructura: bug en otro lado, no error de validación
        return jsonify({
            "errors": [{
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Ocurrió un error inesperado",
                "level": "error",
                "description": str(e),
            }]
        }), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        return jsonify({
            "errors": [{
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Ocurrió un error inesperado",
                "description": str(e)
            }]
        }), 500