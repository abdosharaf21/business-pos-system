"""Flask application entry point."""

import os
import sys
import atexit
import logging
from datetime import timedelta

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cwd = os.getcwd()


def _candidate_env_files():
    """Return the ordered list of .env file paths to try.

    Packaged app places the .env at ``resources/.env`` next to the
    executable; development places it at the project root.
    """
    candidates = []
    env_file = os.environ.get("ENV_FILE")
    if env_file:
        candidates.append(env_file)
    candidates.extend([
        os.path.join(_cwd, '.env'),
        os.path.join(_cwd, 'resources', '.env'),
        os.path.join(_project_root, '.env'),
        os.path.join(_project_root, 'resources', '.env'),
        os.path.normpath(os.path.join(_project_root, '..', '.env')),
    ])
    return candidates


_env_debug = []
for _env_path in _candidate_env_files():
    _env_debug.append(f"checking: {_env_path} exists={os.path.isfile(_env_path)}")
    if os.path.isfile(_env_path):
        with open(_env_path, encoding='utf-8-sig') as _f:
            for _line in _f:
                _line = _line.strip()
                if not _line or _line.startswith('#'):
                    continue
                if '=' in _line:
                    _k, _v = _line.split('=', 1)
                    _k, _v = _k.strip().lstrip('\ufeff').strip('"\''), _v.strip().strip('"\'')
                    if _k and _k not in os.environ:
                        os.environ[_k] = _v
_env_debug.append(f"SECRET_KEY in environ: {'SECRET_KEY' in os.environ}")
try:
    with open(os.path.join(_cwd, 'env_debug.log'), 'w') as _f:
        _f.write('\n'.join(_env_debug))
except OSError:
    pass
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from flask import Flask, jsonify, request, g, send_from_directory
from flask_jwt_extended import JWTManager

from backend.config import get_config
from backend.database import Database
from backend.database.bootstrap import BootstrapError, ensure_database_ready
from backend import setup_server

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

from backend.modules.expenses.routes import expenses_bp, init_expense_service
from backend.modules.expenses.repository import ExpenseRepository
from backend.modules.expenses.service import ExpenseService

from backend.modules.inventory_audits.routes import (
    inventory_audits_bp,
    init_audit_service,
)
from backend.modules.inventory_audits.repository import InventoryAuditRepository
from backend.modules.inventory_audits.service import InventoryAuditService

from backend.modules.notifications.routes import (
    notifications_bp,
    init_notification_service,
)
from backend.modules.notifications.repository import NotificationRepository
from backend.modules.notifications.service import NotificationService

from backend.modules.store_settings.routes import (
    store_settings_bp,
    init_store_settings_service,
)
from backend.modules.store_settings.repository import StoreSettingsRepository
from backend.modules.store_settings.service import StoreSettingsService

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


def _startup_error_dir() -> str:
    """Return the directory used for the startup error diagnostic file.

    Returns:
        Directory path (resources dir in the packaged app, CWD otherwise).
    """
    env_file = os.environ.get("ENV_FILE")
    if env_file:
        return os.path.dirname(env_file)
    return _cwd


def _write_startup_error_file(error: BootstrapError) -> None:
    """Persist the bootstrap error for diagnostic purposes.

    Args:
        error: The bootstrap failure to record.
    """
    try:
        target = os.path.join(_startup_error_dir(), "startup_error.txt")
        with open(target, "w", encoding="utf-8") as f:
            f.write(error.message + "\n\n" + error.instructions)
        logger.error("Startup error written to %s", target)
    except OSError as e:
        logger.warning("Could not write startup error file: %s", e)


def create_app(config: dict = None, bootstrap: bool = False) -> Flask:
    """Create and configure the Flask application.

    Args:
        config: Optional configuration dictionary.
        bootstrap: Whether to run the idempotent database bootstrap
            (schema reconcile + admin seeding) before wiring services.
            Used by the WSGI entrypoint; defaults to False to preserve
            the desktop startup flow.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    config_class = get_config()
    config_class.validate()

    log_level = getattr(logging, config_class.LOG_LEVEL.upper(), logging.INFO)
    logging.getLogger().setLevel(log_level)
    logger.info("Log level set to %s", config_class.LOG_LEVEL.upper())

    app.config["SECRET_KEY"] = config_class.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = config_class.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=config_class.JWT_ACCESS_TOKEN_EXPIRES)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=config_class.JWT_REFRESH_TOKEN_EXPIRES)
    app.config["JWT_TOKEN_LOCATION"] = config_class.JWT_TOKEN_LOCATION
    app.config["JWT_HEADER_NAME"] = config_class.JWT_HEADER_NAME
    app.config["JWT_HEADER_TYPE"] = config_class.JWT_HEADER_TYPE
    app.config["MAX_CONTENT_LENGTH"] = config_class.MAX_CONTENT_LENGTH
    app.config["DEBUG"] = config_class.DEBUG
    app.config["SECURITY_HEADERS_ENABLED"] = config_class.SECURITY_HEADERS_ENABLED
    app.config["CSP_ENABLED"] = config_class.CSP_ENABLED
    app.config["CSP_POLICY"] = config_class.CSP_POLICY
    app.config["HSTS_ENABLED"] = config_class.HSTS_ENABLED
    app.config["CORS_ORIGINS"] = config_class.CORS_ORIGINS
    app.config["CORS_EXPAND_LAN"] = config_class.CORS_EXPAND_LAN

    if config:
        app.config.update(config)

    if bootstrap:
        try:
            bootstrap_result = ensure_database_ready()
            logger.info("Database bootstrap complete: %s", bootstrap_result)
        except BootstrapError as bootstrap_error:
            logger.error(
                "Database bootstrap failed: %s (%s)",
                bootstrap_error.message,
                bootstrap_error.instructions,
            )
            raise

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
    register_cors(
        app,
        allowed_origins=app.config.get("CORS_ORIGINS"),
        expand_lan=app.config.get("CORS_EXPAND_LAN", True),
    )

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

    expense_repo = ExpenseRepository(database)
    expense_service = ExpenseService(expense_repo)
    init_expense_service(expense_service)

    audit_repo = InventoryAuditRepository(database)
    audit_service = InventoryAuditService(audit_repo)
    init_audit_service(audit_service)

    report_repo = ReportRepository(database)
    report_service = ReportService(report_repo, expense_repo, audit_repo)
    init_report_service(report_service)

    notification_repo = NotificationRepository(database)
    notification_service = NotificationService(notification_repo)
    init_notification_service(notification_service)

    store_settings_repo = StoreSettingsRepository(database)
    store_settings_service = StoreSettingsService(store_settings_repo)
    init_store_settings_service(store_settings_service)

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
    app.register_blueprint(expenses_bp)
    app.register_blueprint(inventory_audits_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(store_settings_bp)

    @app.get("/api/setup/status")
    def setup_status():
        """Signal that the normal application is ready (no setup needed)."""
        return jsonify({"success": True, "setup_required": False})

    if config_class.SERVE_STATIC:
        frontend_dir = config_class.FRONTEND_DIST
        if os.path.isdir(frontend_dir):
            logger.info("Serving static frontend from %s", frontend_dir)

            @app.route("/", defaults={"path": ""})
            @app.route("/<path:path>")
            def serve_frontend(path):
                """Serve React SPA or static assets.

                Args:
                    path: URL path to serve.

                Returns:
                    Static file or index.html for client-side routing.
                """
                if path.startswith("api/"):
                    return jsonify({"success": False, "message": "Not found"}), 404
                file_path = os.path.join(frontend_dir, path)
                if path and os.path.isfile(file_path):
                    return send_from_directory(frontend_dir, path)
                return send_from_directory(frontend_dir, "index.html")
        else:
            logger.warning(
                "Frontend dist not found at %s; static serving disabled",
                frontend_dir,
            )

    return app


if __name__ == "__main__":
    config_class = get_config()

    try:
        bootstrap_result = ensure_database_ready()
        logger.info("Database bootstrap complete: %s", bootstrap_result)
    except BootstrapError as bootstrap_error:
        _write_startup_error_file(bootstrap_error)
        logger.error(
            "Database setup required (%s); starting setup wizard", bootstrap_error.message
        )
        setup_app = setup_server.create_setup_app(
            env_file=os.environ.get("ENV_FILE"),
        )
        setup_app.run(
            host=config_class.SERVER_HOST,
            port=config_class.SERVER_PORT,
            debug=False,
        )
        sys.exit(3)

    application = create_app()
    application.run(
        debug=config_class.DEBUG,
        host=config_class.SERVER_HOST,
        port=config_class.SERVER_PORT,
    )
