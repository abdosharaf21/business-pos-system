"""Flask application entry point for Worker Management + Expenses standalone."""

import os
import sys
import atexit
import logging
from datetime import timedelta

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cwd = os.getcwd()

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from flask import Flask, jsonify, request, g, send_from_directory
from flask_jwt_extended import JWTManager

from backend.config import get_config
from backend.database import Database
from backend.database.bootstrap import BootstrapError, ensure_database_ready

from backend.modules.users.routes import users_bp, init_user_service
from backend.modules.dashboard.routes import dashboard_bp, init_dashboard_service
from backend.modules.auth.routes import auth_bp, init_auth_service
from backend.modules.auth.repository import AuthRepository
from backend.modules.auth.service import AuthService

from backend.modules.users.repository import UserRepository
from backend.modules.users.service import UserService
from backend.modules.users.model import User

from backend.modules.dashboard.service import DashboardService

from backend.modules.expenses.routes import expenses_bp, init_expense_service
from backend.modules.expenses.repository import ExpenseRepository
from backend.modules.expenses.service import ExpenseService

from backend.modules.store_settings.routes import (
    store_settings_bp,
    init_store_settings_service,
)
from backend.modules.store_settings.repository import StoreSettingsRepository
from backend.modules.store_settings.service import StoreSettingsService

from backend.modules.worker_management.routes import (
    worker_management_bp,
    init_worker_management_service,
)
from backend.modules.worker_management.repository import (
    AdvanceRepository,
    AttendanceRepository,
    SalaryRepository,
    WorkerManagementRepository,
    WorkerRepository,
)
from backend.modules.worker_management.service import WorkerManagementService

from backend.modules.reports.routes import reports_bp, init_report_service
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


def _startup_error_dir() -> str:
    """Return the directory used for the startup error diagnostic file.

    Returns:
        Directory path used for the startup error diagnostic file.
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
            Used by the WSGI entrypoint; defaults to False for the
            standalone ``python app.py`` dev flow.

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

    worker_management_repo = WorkerManagementRepository(database)
    expense_repo = ExpenseRepository(database)
    dashboard_service = DashboardService(
        worker_management_repository=worker_management_repo,
        expense_repository=expense_repo,
    )
    init_dashboard_service(dashboard_service)

    expense_service = ExpenseService(expense_repo)
    init_expense_service(expense_service)

    store_settings_repo = StoreSettingsRepository(database)
    store_settings_service = StoreSettingsService(store_settings_repo)
    init_store_settings_service(store_settings_service)

    worker_repo = WorkerRepository(database)
    attendance_repo = AttendanceRepository(database)
    salary_repo = SalaryRepository(database)
    advance_repo = AdvanceRepository(database)
    worker_management_service = WorkerManagementService(
        worker_repo,
        attendance_repo,
        salary_repo,
        advance_repo,
        worker_management_repo,
    )
    init_worker_management_service(worker_management_service)

    report_service = ReportService(expense_repo)
    init_report_service(report_service)

    atexit.register(database.close_all)

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(store_settings_bp)
    app.register_blueprint(worker_management_bp)
    app.register_blueprint(reports_bp)

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
            "Database setup required (%s); failing fast. "
            "Configure the DB_* environment variables and retry.",
            bootstrap_error.message,
        )
        sys.exit(3)

    application = create_app()
    application.run(
        debug=config_class.DEBUG,
        host=config_class.SERVER_HOST,
        port=config_class.SERVER_PORT,
    )