"""Flask application entry point."""

import os
import sys
import atexit
import logging
from datetime import timedelta

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from flask import Flask, jsonify, request, g
from flask_jwt_extended import JWTManager

from backend.config import get_config
from backend.database import Database

from backend.modules.users.routes import users_bp, init_user_service
from backend.modules.clients.routes import clients_bp, init_client_service
from backend.modules.services.routes import services_bp, init_service_service
from backend.modules.service_categories.routes import service_categories_bp, init_category_service
from backend.modules.client_services.routes import client_services_bp, init_assignment_service
from backend.modules.dashboard.routes import dashboard_bp, init_dashboard_service
from backend.modules.auth.routes import auth_bp, init_auth_service
from backend.modules.auth.repository import AuthRepository
from backend.modules.auth.service import AuthService

from backend.modules.users.repository import UserRepository
from backend.modules.users.service import UserService
from backend.modules.users.model import User

from backend.modules.clients.repository import ClientRepository
from backend.modules.clients.service import ClientService

from backend.modules.services.repository import ServiceRepository
from backend.modules.services.service import ServiceService

from backend.modules.service_categories.repository import ServiceCategoryRepository
from backend.modules.service_categories.service import ServiceCategoryService

from backend.modules.client_services.repository import ClientServiceRepository
from backend.modules.client_services.service import ClientServiceAssignmentService

from backend.modules.dashboard.service import DashboardService

from backend.middleware import (
    register_error_handlers,
    register_security_headers,
    register_cors,
    start_timer,
    get_request_duration,
    log_request,
    log_response,
    load_user_context,
)

from backend.docs import get_swagger_ui_response, get_spec_json_response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

jwt_blocklist = set()


def create_app(config: dict = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config: Optional configuration dictionary.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    config_class = get_config()
    config_class.validate()

    app.config["SECRET_KEY"] = config_class.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = config_class.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=config_class.JWT_ACCESS_TOKEN_EXPIRES)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=config_class.JWT_REFRESH_TOKEN_EXPIRES)
    app.config["JWT_TOKEN_LOCATION"] = config_class.JWT_TOKEN_LOCATION
    app.config["JWT_HEADER_NAME"] = config_class.JWT_HEADER_NAME
    app.config["JWT_HEADER_TYPE"] = config_class.JWT_HEADER_TYPE
    app.config["MAX_CONTENT_LENGTH"] = config_class.MAX_CONTENT_LENGTH
    app.config["DEBUG"] = config_class.DEBUG

    if config:
        app.config.update(config)

    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if JWT token has been revoked.

        Args:
            jwt_header: JWT header.
            jwt_payload: JWT payload.

        Returns:
            True if token is revoked, False otherwise.
        """
        jti = jwt_payload["jti"]
        return jti in jwt_blocklist

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired JWT token.

        Args:
            jwt_header: JWT header.
            jwt_payload: JWT payload.

        Returns:
            JSON error response.
        """
        return jsonify({
            "success": False,
            "message": "Token has expired",
            "status": 401
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        """Handle invalid JWT token.

        Args:
            error_string: Error description.

        Returns:
            JSON error response.
        """
        return jsonify({
            "success": False,
            "message": "Invalid token",
            "status": 401
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        """Handle missing JWT token.

        Args:
            error_string: Error description.

        Returns:
            JSON error response.
        """
        return jsonify({
            "success": False,
            "message": "Authorization token is required",
            "status": 401
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Handle revoked JWT token.

        Args:
            jwt_header: JWT header.
            jwt_payload: JWT payload.

        Returns:
            JSON error response.
        """
        return jsonify({
            "success": False,
            "message": "Token has been revoked",
            "status": 401
        }), 401

    register_error_handlers(app)
    register_security_headers(app)
    register_cors(app)

    @app.before_request
    def before_request():
        """Execute before each request."""
        start_timer()
        log_request(request)
        load_user_context()

    @app.after_request
    def after_request(response):
        """Execute after each request.

        Args:
            response: Flask response object.

        Returns:
            Modified response with timing header.
        """
        duration = get_request_duration()
        response.headers["X-Request-Duration"] = f"{duration:.4f}s"
        log_response(response, g.get("start_time", 0))
        return response

    @app.teardown_appcontext
    def teardown_context(exception):
        """Clean up at the end of each request.

        Args:
            exception: Any exception that occurred during request.
        """
        pass

    database = Database()

    user_repo = UserRepository(database)
    user_service = UserService(user_repo, jwt_blocklist)
    init_user_service(user_service, jwt_blocklist)

    auth_repo = AuthRepository(database)
    auth_service = AuthService(auth_repo, user_repo)
    init_auth_service(auth_service)

    client_repo = ClientRepository(database)
    client_service = ClientService(client_repo)
    init_client_service(client_service)

    service_repo = ServiceRepository(database)
    service_service = ServiceService(service_repo)
    init_service_service(service_service)

    category_repo = ServiceCategoryRepository(database)
    category_service = ServiceCategoryService(category_repo)
    init_category_service(category_service)

    assignment_repo = ClientServiceRepository(database)
    assignment_service = ClientServiceAssignmentService(assignment_repo)
    init_assignment_service(assignment_service)

    dashboard_service = DashboardService(
        user_repository=user_repo,
        client_repository=client_repo,
        service_repository=service_repo,
        category_repository=category_repo
    )
    init_dashboard_service(dashboard_service)

    atexit.register(database.close_all)

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(service_categories_bp)
    app.register_blueprint(client_services_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/api/docs", methods=["GET"])
    def swagger_ui():
        """Serve Swagger UI for API documentation.

        Returns:
            HTML response with Swagger UI interface.
        """
        return get_swagger_ui_response()

    @app.route("/api/docs/spec.json", methods=["GET"])
    def openapi_spec():
        """Serve the OpenAPI 3.0 specification as JSON.

        Returns:
            JSON response with the complete API specification.
        """
        return get_spec_json_response()

    return app


if __name__ == "__main__":
    config_class = get_config()
    application = create_app()
    application.run(debug=config_class.DEBUG, host="0.0.0.0", port=5000)
