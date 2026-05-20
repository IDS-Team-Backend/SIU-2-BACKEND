from flask import app, jsonify


def created_response(body, resource_path):
    response = jsonify(body)
    response.headers["Location"] = resource_path
    return response, 201

class NotFoundError(Exception): pass
class ValidationError(Exception): pass
class DuplicateError(Exception): pass


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

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({
            "errors": [
                {
                    "code": "BAD_REQUEST",
                    "message": str(e),
                    "level": "error",
                    "description": str(e),
                }
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

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        return jsonify({
            "errors": [{
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Ocurrió un error inesperado",
                "description": str(e)
            }]
        }), 500