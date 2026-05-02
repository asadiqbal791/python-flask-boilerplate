import traceback
from http import HTTPStatus
from flask import jsonify, current_app
from marshmallow import ValidationError as MarshmallowValidationError
from flask_jwt_extended.exceptions import JWTExtendedException
from app.utils.api_error import ApiError


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(err: ApiError):
        return jsonify({
            "success": False,
            "message": err.message,
            "statusCode": err.status_code,
        }), err.status_code

    @app.errorhandler(MarshmallowValidationError)
    def handle_validation_error(err: MarshmallowValidationError):
        return jsonify({
            "success": False,
            "message": "Validation error",
            "errors": err.messages,
            "statusCode": HTTPStatus.BAD_REQUEST,
        }), HTTPStatus.BAD_REQUEST

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(err):
        return jsonify({
            "success": False,
            "message": "Please authenticate",
            "statusCode": HTTPStatus.UNAUTHORIZED,
        }), HTTPStatus.UNAUTHORIZED

    @app.errorhandler(404)
    def handle_404(_err):
        return jsonify({
            "success": False,
            "message": "Not found",
            "statusCode": HTTPStatus.NOT_FOUND,
        }), HTTPStatus.NOT_FOUND

    @app.errorhandler(405)
    def handle_405(_err):
        return jsonify({
            "success": False,
            "message": "Method not allowed",
            "statusCode": HTTPStatus.METHOD_NOT_ALLOWED,
        }), HTTPStatus.METHOD_NOT_ALLOWED

    @app.errorhandler(Exception)
    def handle_unhandled(err: Exception):
        current_app.logger.error("Unhandled exception: %s\n%s", err, traceback.format_exc())
        if current_app.config.get("DEBUG"):
            message = str(err)
        else:
            message = "Internal server error"
        return jsonify({
            "success": False,
            "message": message,
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
        }), HTTPStatus.INTERNAL_SERVER_ERROR
