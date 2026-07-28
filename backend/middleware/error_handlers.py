"""Global error handlers for Flask application."""

import logging
import mysql.connector
from flask import Flask, jsonify, request

from backend.middleware.exceptions import (
    AppException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    ValidationException,
    DatabaseException,
    ServiceUnavailableException
)

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    """Register global error handlers for the Flask application.

    Args:
        app: Flask application instance.
    """

    @app.errorhandler(BadRequestException)
    def handle_bad_request(error):
        """Handle BadRequestException (400).

        Args:
            error: BadRequestException that occurred.

        Returns:
            JSON error response with 400 status.
        """
        logger.warning(
            "Bad request: %s %s - %s",
            request.method,
            request.url,
            error.message
        )
        return jsonify(error.to_dict()), 400

    @app.errorhandler(UnauthorizedException)
    def handle_unauthorized(error):
        """Handle UnauthorizedException (401).

        Args:
            error: UnauthorizedException that occurred.

        Returns:
            JSON error response with 401 status.
        """
        logger.warning(
            "Unauthorized: %s %s - %s",
            request.method,
            request.url,
            error.message
        )
        return jsonify(error.to_dict()), 401

    @app.errorhandler(ForbiddenException)
    def handle_forbidden(error):
        """Handle ForbiddenException (403).

        Args:
            error: ForbiddenException that occurred.

        Returns:
            JSON error response with 403 status.
        """
        logger.warning(
            "Forbidden: %s %s - %s",
            request.method,
            request.url,
            error.message
        )
        return jsonify(error.to_dict()), 403

    @app.errorhandler(NotFoundException)
    def handle_not_found(error):
        """Handle NotFoundException (404).

        Args:
            error: NotFoundException that occurred.

        Returns:
            JSON error response with 404 status.
        """
        logger.warning(
            "Not found: %s %s - %s",
            request.method,
            request.url,
            error.message
        )
        return jsonify(error.to_dict()), 404

    @app.errorhandler(ConflictException)
    def handle_conflict(error):
        """Handle ConflictException (409).

        Args:
            error: ConflictException that occurred.

        Returns:
            JSON error response with 409 status.
        """
        logger.warning(
            "Conflict: %s %s - %s",
            request.method,
            request.url,
            error.message
        )
        return jsonify(error.to_dict()), 409

    @app.errorhandler(ValidationException)
    def handle_validation(error):
        """Handle ValidationException (422).

        Args:
            error: ValidationException that occurred.

        Returns:
            JSON error response with 422 status.
        """
        logger.warning(
            "Validation error: %s %s - %s",
            request.method,
            request.url,
            error.message
        )
        return jsonify(error.to_dict()), 422

    @app.errorhandler(DatabaseException)
    def handle_database(error):
        """Handle DatabaseException (500).

        Args:
            error: DatabaseException that occurred.

        Returns:
            JSON error response with 500 status.
        """
        logger.error(
            "Database error: %s %s - %s",
            request.method,
            request.url,
            error.message,
            exc_info=True
        )
        return jsonify(error.to_dict()), 500

    @app.errorhandler(mysql.connector.Error)
    def handle_mysql_error(error):
        """Handle raw MySQL errors that escape repository layer.

        Logs the full error internally but returns a generic message
        to prevent SQL details from reaching API responses.

        Args:
            error: mysql.connector.Error that occurred.

        Returns:
            JSON error response with 500 status.
        """
        logger.error(
            "MySQL error: %s %s - %s",
            request.method,
            request.url,
            str(error),
            exc_info=True
        )
        return jsonify({
            "success": False,
            "message": "A database error occurred",
            "status": 500
        }), 500

    @app.errorhandler(ServiceUnavailableException)
    def handle_service_unavailable(error):
        """Handle ServiceUnavailableException (503).

        Args:
            error: ServiceUnavailableException that occurred.

        Returns:
            JSON error response with 503 status.
        """
        logger.error(
            "Service unavailable: %s %s - %s",
            request.method,
            request.url,
            error.message
        )
        return jsonify(error.to_dict()), 503

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        """Handle ValueError (400).

        Args:
            error: ValueError that occurred.

        Returns:
            JSON error response with 400 status.
        """
        logger.warning(
            "Value error: %s %s - %s",
            request.method,
            request.url,
            str(error)
        )
        return jsonify({
            "success": False,
            "message": str(error),
            "status": 400
        }), 400

    @app.errorhandler(KeyError)
    def handle_key_error(error):
        """Handle KeyError (400).

        Args:
            error: KeyError that occurred.

        Returns:
            JSON error response with 400 status.
        """
        logger.warning(
            "Key error: %s %s - Missing key: %s",
            request.method,
            request.url,
            str(error)
        )
        return jsonify({
            "success": False,
            "message": f"Missing required field: {str(error)}",
            "status": 400
        }), 400

    @app.errorhandler(PermissionError)
    def handle_permission_error(error):
        """Handle PermissionError (403).

        Args:
            error: PermissionError that occurred.

        Returns:
            JSON error response with 403 status.
        """
        logger.warning(
            "Permission error: %s %s - %s",
            request.method,
            request.url,
            str(error)
        )
        return jsonify({
            "success": False,
            "message": "Permission denied",
            "status": 403
        }), 403

    @app.errorhandler(FileNotFoundError)
    def handle_file_not_found(error):
        """Handle FileNotFoundError (404).

        Args:
            error: FileNotFoundError that occurred.

        Returns:
            JSON error response with 404 status.
        """
        logger.warning(
            "File not found: %s %s - %s",
            request.method,
            request.url,
            str(error)
        )
        return jsonify({
            "success": False,
            "message": "File not found",
            "status": 404
        }), 404

    @app.errorhandler(400)
    def handle_400(error):
        """Handle 400 Bad Request.

        Args:
            error: The error that occurred.

        Returns:
            JSON error response with 400 status.
        """
        logger.warning(
            "Bad request: %s %s - %s",
            request.method,
            request.url,
            str(error)
        )
        return jsonify({
            "success": False,
            "message": "Bad request",
            "status": 400
        }), 400

    @app.errorhandler(401)
    def handle_401(error):
        """Handle 401 Unauthorized.

        Args:
            error: The error that occurred.

        Returns:
            JSON error response with 401 status.
        """
        logger.warning(
            "Unauthorized: %s %s",
            request.method,
            request.url
        )
        return jsonify({
            "success": False,
            "message": "Unauthorized",
            "status": 401
        }), 401

    @app.errorhandler(403)
    def handle_403(error):
        """Handle 403 Forbidden.

        Args:
            error: The error that occurred.

        Returns:
            JSON error response with 403 status.
        """
        logger.warning(
            "Forbidden: %s %s",
            request.method,
            request.url
        )
        return jsonify({
            "success": False,
            "message": "Access denied",
            "status": 403
        }), 403

    @app.errorhandler(404)
    def handle_404(error):
        """Handle 404 Not Found.

        Args:
            error: The error that occurred.

        Returns:
            JSON error response with 404 status.
        """
        logger.warning(
            "Not found: %s %s",
            request.method,
            request.url
        )
        return jsonify({
            "success": False,
            "message": "Resource not found",
            "status": 404
        }), 404

    @app.errorhandler(405)
    def handle_405(error):
        """Handle 405 Method Not Allowed.

        Args:
            error: The error that occurred.

        Returns:
            JSON error response with 405 status.
        """
        logger.warning(
            "Method not allowed: %s %s",
            request.method,
            request.url
        )
        return jsonify({
            "success": False,
            "message": "Method not allowed",
            "status": 405
        }), 405

    @app.errorhandler(409)
    def handle_409(error):
        """Handle 409 Conflict.

        Args:
            error: The error that occurred.

        Returns:
            JSON error response with 409 status.
        """
        logger.warning(
            "Conflict: %s %s",
            request.method,
            request.url
        )
        return jsonify({
            "success": False,
            "message": "Resource conflict",
            "status": 409
        }), 409

    @app.errorhandler(422)
    def handle_422(error):
        """Handle 422 Unprocessable Entity.

        Args:
            error: The error that occurred.

        Returns:
            JSON error response with 422 status.
        """
        logger.warning(
            "Unprocessable entity: %s %s",
            request.method,
            request.url
        )
        return jsonify({
            "success": False,
            "message": "Unprocessable entity",
            "status": 422
        }), 422

    @app.errorhandler(429)
    def handle_429(error):
        """Handle 429 Too Many Requests.

        Args:
            error: The error that occurred.

        Returns:
            JSON error response with 429 status.
        """
        logger.warning(
            "Rate limit exceeded: %s %s",
            request.method,
            request.url
        )
        return jsonify({
            "success": False,
            "message": "Too many requests",
            "status": 429
        }), 429

    @app.errorhandler(500)
    def handle_500(error):
        """Handle 500 Internal Server Error.

        Args:
            error: The error that occurred.

        Returns:
            JSON error response with 500 status.
        """
        logger.error(
            "Internal server error: %s %s - %s",
            request.method,
            request.url,
            str(error),
            exc_info=True
        )
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "status": 500
        }), 500

    @app.errorhandler(502)
    def handle_502(error):
        """Handle 502 Bad Gateway.

        Args:
            error: The error that occurred.

        Returns:
            JSON error response with 502 status.
        """
        logger.error(
            "Bad gateway: %s %s",
            request.method,
            request.url
        )
        return jsonify({
            "success": False,
            "message": "Bad gateway",
            "status": 502
        }), 502

    @app.errorhandler(503)
    def handle_503(error):
        """Handle 503 Service Unavailable.

        Args:
            error: The error that occurred.

        Returns:
            JSON error response with 503 status.
        """
        logger.error(
            "Service unavailable: %s %s",
            request.method,
            request.url
        )
        return jsonify({
            "success": False,
            "message": "Service unavailable",
            "status": 503
        }), 503

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        """Handle all unexpected exceptions.

        Args:
            error: The exception that occurred.

        Returns:
            JSON error response with 500 status.
        """
        logger.error(
            "Unexpected error: %s %s - %s",
            request.method,
            request.url,
            str(error),
            exc_info=True
        )
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred",
            "status": 500
        }), 500
