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
from backend.modules.dashboard.routes import dashboard_bp, init_dashboard_service
from backend.modules.auth.routes import auth_bp, init_auth_service
from backend.modules.auth.repository import AuthRepository
from backend.modules.auth.service import AuthService

from backend.modules.users.repository import UserRepository
from backend.modules.users.service import UserService
from backend.modules.users.model import User

from backend.modules.dashboard.repository import DashboardRepository
from backend.modules.dashboard.service import DashboardService

from backend.modules.categories.routes import categories_bp, init_category_service as init_pos_category_service
from backend.modules.categories.repository import CategoryRepository
from backend.modules.categories.service import CategoryService

from backend.modules.inventory.routes import inventory_bp, init_inventory_service
from backend.modules.inventory.repository import InventoryRepository
from backend.modules.inventory.service import InventoryService

from backend.modules.products.routes import products_bp, init_product_service
from backend.modules.products.repository import ProductRepository
from backend.modules.products.service import ProductService

from backend.modules.customers.routes import customers_bp, init_customer_service
from backend.modules.customers.repository import CustomerRepository
from backend.modules.customers.service import CustomerService

from backend.modules.purchases.routes import (
    purchases_bp, suppliers_bp, init_purchase_service,
)
from backend.modules.purchases.repository import PurchaseRepository
from backend.modules.purchases.service import PurchaseService

from backend.modules.pos.routes import pos_bp, init_pos_service
from backend.modules.pos.repository import PosRepository
from backend.modules.pos.service import PosService

from backend.modules.reports.routes import reports_bp, init_report_service
from backend.modules.reports.repository import ReportRepository
from backend.modules.reports.service import ReportService

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
    auth_service = AuthService(auth_repo, user_repo, jwt_blocklist)
    init_auth_service(auth_service)

    dashboard_repo = DashboardRepository(database)
    dashboard_service = DashboardService(dashboard_repository=dashboard_repo)
    init_dashboard_service(dashboard_service)

    pos_category_repo = CategoryRepository(database)
    pos_category_service = CategoryService(pos_category_repo)
    init_pos_category_service(pos_category_service)

    inventory_repo = InventoryRepository(database)
    inventory_service = InventoryService(inventory_repo)
    init_inventory_service(inventory_service)

    product_repo = ProductRepository(database)
    product_service = ProductService(product_repo, pos_category_repo)
    init_product_service(product_service)

    customer_repo = CustomerRepository(database)
    customer_service = CustomerService(customer_repo)
    init_customer_service(customer_service)

    purchase_repo = PurchaseRepository(database)
    purchase_service = PurchaseService(purchase_repo)
    init_purchase_service(purchase_service)

    pos_repo = PosRepository(database)
    pos_service = PosService(pos_repo)
    init_pos_service(pos_service)

    report_repo = ReportRepository(database)
    report_service = ReportService(report_repo)
    init_report_service(report_service)

    atexit.register(database.close_all)

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(reports_bp)

    return app


if __name__ == "__main__":
    config_class = get_config()
    application = create_app()
    application.run(debug=config_class.DEBUG, host="0.0.0.0", port=5001)
