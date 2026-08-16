"""First-run database bootstrap and schema migration for the application.

Responsible for detecting MySQL Server, creating the configured database
when it is missing, importing the matching schema/seed file for a
brand-new database, reconciling an existing database against the bundled
schema (adding missing tables and columns without touching existing
data), and ensuring the default admin user exists.

The schema file is chosen by database name so each standalone service
database (``pos_system``, ``worker_management``) is bootstrapped from
its own file under ``db/``.

The bootstrap is intentionally idempotent and non-destructive:

* An existing database is reconciled forward: missing tables are created
  and missing columns are added, but existing data is never altered,
  dropped, or overwritten.
* A database that is newly created but fails to import is dropped again
  so the next launch retries cleanly instead of leaving a partial schema.
* The admin user is only inserted when it does not already exist.
"""

import os
import re
import logging

import mysql.connector

from backend.database.config import get_database_config, DatabaseConfig

logger = logging.getLogger(__name__)

_SCHEMA_FILES = {
    "pos_system": os.path.join("db", "pos_system.sql"),
    "worker_management": os.path.join("db", "worker_management.sql"),
}

ADMIN_EMAIL = "admin@pos.com"
ADMIN_FULL_NAME = "Admin User"
ADMIN_PASSWORD_HASH = (
    "$2b$12$rowv6gy8.CmyHXxQmdGZiOoMA2JxHJML88kLXghUb78tr/LSLlcwm"
)
ADMIN_PHONE = "+10000000000"
ADMIN_ROLE = "admin"
ADMIN_STATUS = "active"

MYSQL_NOT_DETECTED = (
    "The Business POS System could not connect to MySQL Server at "
    "{host}:{port}.\n\n"
    "MySQL Server does not appear to be installed or the service is not running.\n\n"
    "To install MySQL:\n"
    "  1. Download 'MySQL Community Server 8.0' from "
    "https://dev.mysql.com/downloads/mysql/\n"
    "  2. Run the installer and choose 'Server only' (or Developer Default).\n"
    "  3. When prompted, create a root password and keep it somewhere safe.\n"
    "  4. After installation, open Windows Services and make sure the "
    "MySQL80 service is running.\n"
    "  5. Open the application configuration file and set DB_USER / "
    "DB_PASSWORD to match your MySQL account:\n"
    "     {env_file}\n"
    "  6. Reopen the application. It will create the database automatically."
)

ACCESS_DENIED = (
    "MySQL Server is reachable, but the database login was rejected "
    "(Access denied for user).\n\n"
    "Open the application configuration file and set DB_USER / DB_PASSWORD "
    "to match your MySQL account, then reopen the application:\n"
    "     {env_file}"
)

GENERIC_ERROR = (
    "The application could not prepare the database.\n\n"
    "Details:\n{detail}\n\n"
    "If this keeps happening, contact your administrator."
)


class BootstrapError(Exception):
    """Raised when first-run database setup cannot complete.

    Attributes:
        message: Short description of the failure.
        instructions: Human-readable instructions for the user.
    """

    def __init__(self, message: str, instructions: str = None) -> None:
        """Initialize the bootstrap error.

        Args:
            message: Short description of the failure.
            instructions: Human-readable instructions; defaults to message.
        """
        super().__init__(message)
        self.message = message
        self.instructions = instructions or message


def _env_file_for_message() -> str:
    """Return the path of the active .env file for user-facing messages.

    Returns:
        The .env path that is most likely the one the user can edit.
    """
    env_file = os.environ.get("ENV_FILE")
    if env_file:
        return env_file
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "resources", ".env"),
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return env_file or os.path.join(os.getcwd(), "resources", ".env")


def _map_connect_error(error: mysql.connector.Error, config: DatabaseConfig) -> BootstrapError:
    """Convert a connection failure into a user-friendly BootstrapError.

    Args:
        error: The mysql.connector error raised while connecting.
        config: The database configuration that failed.

    Returns:
        A BootstrapError with targeted instructions.
    """
    if error.errno in (2002, 2003, 2005, 2006):
        return BootstrapError(
            f"MySQL server is not reachable at {config.host}:{config.port}.",
            instructions=MYSQL_NOT_DETECTED.format(
                host=config.host,
                port=config.port,
                env_file=_env_file_for_message(),
            ),
        )
    if error.errno == 1045:
        return BootstrapError(
            "MySQL rejected the configured database credentials.",
            instructions=ACCESS_DENIED.format(env_file=_env_file_for_message()),
        )
    return BootstrapError(
        f"Unexpected MySQL error: {error}",
        instructions=GENERIC_ERROR.format(detail=error),
    )


def _connect_server(config: DatabaseConfig) -> mysql.connector.MySQLConnection:
    """Connect to the MySQL server without selecting a database.

    Args:
        config: The database configuration.

    Returns:
        A server-level connection.

    Raises:
        BootstrapError: If the server cannot be reached or logged into.
    """
    try:
        return mysql.connector.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            connection_timeout=6,
            autocommit=True,
        )
    except mysql.connector.Error as e:
        raise _map_connect_error(e, config) from e


def _database_exists(server: mysql.connector.MySQLConnection, name: str) -> bool:
    """Check whether a database already exists.

    Args:
        server: Server-level connection.
        name: Database name.

    Returns:
        True if the database exists, False otherwise.
    """
    cursor = server.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name=%s",
        (name,),
    )
    exists = bool(cursor.fetchone()[0])
    cursor.close()
    return exists


def _create_database(server: mysql.connector.MySQLConnection, name: str) -> None:
    """Create the database with the project's character set.

    Args:
        server: Server-level connection.
        name: Database name.
    """
    safe_name = name.replace("`", "")
    cursor = server.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{safe_name}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor.close()


def _drop_database(server: mysql.connector.MySQLConnection, name: str) -> None:
    """Drop a database that was created but not fully imported.

    Only safe to call on a database created moments ago by this module;
    it never contains customer data.

    Args:
        server: Server-level connection.
        name: Database name.
    """
    safe_name = name.replace("`", "")
    cursor = server.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS `{safe_name}`")
    cursor.close()


def _find_schema_file(db_name: str = "pos_system") -> str:
    """Locate the bundled schema file across known install layouts.

    Args:
        db_name: Database name used to select the matching schema file
            (``pos_system.sql``, ``worker_management.sql``, ...).

    Returns:
        Absolute path to the matching schema file or None if not found.
    """
    schema_rel = _SCHEMA_FILES.get(db_name, _SCHEMA_FILES["pos_system"])
    schema_name = os.path.basename(schema_rel)
    candidates = []
    env_file = os.environ.get("ENV_FILE")
    if env_file:
        candidates.append(os.path.join(os.path.dirname(env_file), schema_rel))
        candidates.append(os.path.join(os.path.dirname(env_file), schema_name))
    frontend_dist = os.environ.get("FRONTEND_DIST")
    if frontend_dist:
        resources_dir = os.path.dirname(os.path.dirname(frontend_dist))
        candidates.append(os.path.join(resources_dir, schema_rel))
        candidates.append(os.path.join(resources_dir, schema_name))
    cwd = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates.extend([
        os.path.join(cwd, schema_rel),
        os.path.join(cwd, "resources", schema_rel),
        os.path.join(project_root, schema_rel),
        os.path.join(project_root, "resources", schema_rel),
    ])
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


def _load_statements(schema_path: str) -> list:
    """Parse executable SQL statements from the schema file.

    Removes comment lines, the ``CREATE DATABASE`` header and ``USE``
    statements (the target database is selected by the connection), then
    splits the remaining script on statement terminators.

    Args:
        schema_path: Path to the schema file.

    Returns:
        List of executable SQL statements.
    """
    with open(schema_path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    lines = [
        line for line in content.splitlines() if not line.strip().startswith("--")
    ]
    text = "\n".join(lines)
    text = re.sub(r"CREATE DATABASE[^;]*;", "", text, flags=re.I | re.S)
    text = re.sub(r"USE\s+[`'\"]?[\w]+[`'\"]?\s*;", "", text, flags=re.I | re.M)
    return [stmt.strip() for stmt in text.split(";") if stmt.strip()]


def _import_schema(conn: mysql.connector.MySQLConnection, schema_path: str) -> None:
    """Execute all schema statements against the connected database.

    Args:
        conn: Connection to the target database (autocommit on).
        schema_path: Path to the schema file.

    Raises:
        BootstrapError: If any statement fails to execute.
    """
    statements = _load_statements(schema_path)
    if not statements:
        raise BootstrapError(
            "The bundled database schema file is empty or unreadable."
        )
    cursor = conn.cursor()
    for statement in statements:
        try:
            cursor.execute(statement)
        except mysql.connector.Error as e:
            cursor.close()
            raise BootstrapError(
                f"Failed to import schema statement: {e}",
                instructions=GENERIC_ERROR.format(
                    detail=f"{e} -- statement: {statement[:200]}"
                ),
            ) from e
    cursor.close()


_CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+`?(\w+)`?\s*\((.*?)\)\s*ENGINE[^;]*;",
    re.DOTALL | re.IGNORECASE,
)
_CONSTRAINT_PREFIXES = (
    "INDEX", "KEY", "UNIQUE", "CONSTRAINT", "PRIMARY", "FOREIGN",
    "FULLTEXT", "SPATIAL", "REFERENCES", "ON",
)
_SQL_TYPE_KEYWORDS = (
    "INT", "INTEGER", "BIGINT", "SMALLINT", "TINYINT", "MEDIUMINT",
    "DECIMAL", "NUMERIC", "FLOAT", "DOUBLE", "REAL",
    "VARCHAR", "CHAR", "TEXT", "TINYTEXT", "MEDIUMTEXT", "LONGTEXT",
    "DATE", "DATETIME", "TIMESTAMP", "TIME", "YEAR",
    "ENUM", "SET", "JSON", "BLOB", "TINYBLOB", "MEDIUMBLOB", "LONGBLOB",
    "BINARY", "VARBINARY", "BOOLEAN", "BOOL",
)


def _parse_create_statements(schema_path: str) -> dict:
    """Parse the schema file into structured CREATE TABLE definitions.

    Args:
        schema_path: Path to the schema file.

    Returns:
        Dictionary mapping table name to a dict with keys ``create_sql``
        (the raw CREATE TABLE statement) and ``columns`` (list of
        ``(column_name, column_definition)`` tuples).
    """
    with open(schema_path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    tables = {}
    for match in _CREATE_TABLE_RE.finditer(content):
        table_name = match.group(1)
        body = match.group(2)
        create_sql = match.group(0)
        columns = []
        for raw_line in body.splitlines():
            line = raw_line.strip().rstrip(",")
            if not line:
                continue
            tokens = line.split()
            if tokens[0].upper() in _CONSTRAINT_PREFIXES:
                continue
            if len(tokens) < 2:
                continue
            type_base = tokens[1].split("(")[0].upper()
            if type_base not in _SQL_TYPE_KEYWORDS:
                continue
            column_name = tokens[0].strip("`")
            columns.append((column_name, line))
        tables[table_name] = {"create_sql": create_sql, "columns": columns}
    return tables


def _table_exists(conn: mysql.connector.MySQLConnection, name: str) -> bool:
    """Check whether a table exists in the connected database.

    Args:
        conn: Connection to the target database.
        name: Table name.

    Returns:
        True if the table exists, False otherwise.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema = DATABASE() AND table_name = %s",
        (name,),
    )
    exists = bool(cursor.fetchone()[0])
    cursor.close()
    return exists


def _existing_columns(conn: mysql.connector.MySQLConnection, name: str) -> set:
    """Return the column names currently present on a table.

    Args:
        conn: Connection to the target database.
        name: Table name.

    Returns:
        Set of existing column names.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = %s",
        (name,),
    )
    columns = {row[0] for row in cursor.fetchall()}
    cursor.close()
    return columns


def _reconcile_schema(
    conn: mysql.connector.MySQLConnection, schema_path: str
) -> dict:
    """Migrate an existing database forward without touching data.

    Creates any tables declared in the bundled schema that are missing
    and adds any columns missing from existing tables. Existing tables,
    rows, and columns are never altered or dropped.

    Args:
        conn: Connection to the target database (autocommit on).
        schema_path: Path to the schema file.

    Returns:
        Dictionary with keys ``tables_created`` and ``columns_added``.

    Raises:
        BootstrapError: If any migration statement fails to execute.
    """
    tables = _parse_create_statements(schema_path)
    if not tables:
        raise BootstrapError(
            "The bundled database schema file is empty or unreadable."
        )
    cursor = conn.cursor()
    result = {"tables_created": 0, "columns_added": 0}
    try:
        for table_name, definition in tables.items():
            if not _table_exists(conn, table_name):
                cursor.execute(definition["create_sql"])
                result["tables_created"] += 1
                continue
            existing = _existing_columns(conn, table_name)
            for column_name, column_definition in definition["columns"]:
                if column_name in existing:
                    continue
                cursor.execute(
                    "ALTER TABLE `%s` ADD COLUMN %s"
                    % (table_name, column_definition)
                )
                result["columns_added"] += 1
    except mysql.connector.Error as e:
        cursor.close()
        raise BootstrapError(
            f"Failed to reconcile schema: {e}",
            instructions=GENERIC_ERROR.format(detail=str(e)),
        ) from e
    cursor.close()
    return result


def _seed_if_empty(
    conn: mysql.connector.MySQLConnection, table_name: str, insert_sql: str
) -> bool:
    """Insert a seed row only when the target table is empty.

    Args:
        conn: Connection to the target database (autocommit on).
        table_name: Table to check.
        insert_sql: Idempotent INSERT statement to run when empty.

    Returns:
        True if the seed was applied, False otherwise.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM `%s`" % table_name)
        empty = cursor.fetchone()[0] == 0
        if empty:
            cursor.execute(insert_sql)
    finally:
        cursor.close()
    return empty


def _apply_safe_seeds(conn: mysql.connector.MySQLConnection) -> None:
    """Apply seed data that is safe on an existing database.

    Only seeds whose statements are idempotent or guarded by an empty
    check run here; the admin user is handled separately. POS-specific
    seeds (warehouses, expense categories) only run when their tables
    exist in the connected database, so standalone service databases
    (e.g. ``worker_management``) are never touched by POS seeds.

    Args:
        conn: Connection to the target database (autocommit on).
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO store_settings (id, store_name, owner_name, phone, "
        "email, address, website, tax_number, currency, receipt_footer, "
        "logo_path) VALUES (1, '', '', '', '', '', '', '', 'EGP', '', '') "
        "ON DUPLICATE KEY UPDATE id = id"
    )
    if _table_exists(conn, "warehouses"):
        cursor.execute(
            "INSERT INTO warehouses (name, code, address, manager_name, phone, "
            "status) VALUES "
            "('Main Warehouse', 'WH-MAIN', '', '', '', 'active'), "
            "('Store', 'STORE', '', '', '', 'active') "
            "ON DUPLICATE KEY UPDATE id = id"
        )
    cursor.close()
    if _table_exists(conn, "expense_categories"):
        _seed_if_empty(
            conn,
            "expense_categories",
            "INSERT INTO expense_categories (name, description) VALUES "
            "('Rent', 'Payments for business premises'), "
            "('Electricity', 'Electricity and utility bills'), "
            "('Water', 'Water supply bills'), "
            "('Internet', 'Internet and telecommunication bills'), "
            "('Transportation', 'Shipping, delivery and travel costs'), "
            "('Maintenance', 'Equipment and building maintenance'), "
            "('Marketing', 'Advertising and promotional costs'), "
            "('Taxes', 'Tax payments and government fees'), "
            "('Purchases', 'Operational purchases'), "
            "('Salaries', 'Employee wages and salaries'), "
            "('Other', 'Other business expenses')",
        )


def _admin_exists(conn: mysql.connector.MySQLConnection) -> bool:
    """Check whether the default admin user exists.

    Args:
        conn: Connection to the target database.

    Returns:
        True if the admin user exists, False otherwise.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email=%s", (ADMIN_EMAIL,))
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists


def _ensure_admin(conn: mysql.connector.MySQLConnection) -> bool:
    """Create the default admin user if it does not exist.

    Args:
        conn: Connection to the target database.

    Returns:
        True if the admin user is present after the call.
    """
    if _admin_exists(conn):
        return True
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (full_name, email, password_hash, phone, role, status) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (ADMIN_FULL_NAME, ADMIN_EMAIL, ADMIN_PASSWORD_HASH,
         ADMIN_PHONE, ADMIN_ROLE, ADMIN_STATUS),
    )
    conn.commit()
    cursor.close()
    logger.info("Created default admin user %s", ADMIN_EMAIL)
    return True


def ensure_database_ready(config: DatabaseConfig = None) -> dict:
    """Detect MySQL and prepare the database on first run.

    Idempotent: on an existing database it only ensures the default admin
    exists and never re-imports the schema.

    Args:
        config: Optional DatabaseConfig; defaults to environment.

    Returns:
        Dictionary with keys ``database_created``, ``schema_imported``
        and ``admin_present``.

    Raises:
        BootstrapError: If MySQL is unreachable, login fails, or the
            schema import fails.
    """
    config = config or get_database_config()
    result = {
        "database_created": False,
        "schema_imported": False,
        "admin_present": False,
    }
    server = _connect_server(config)
    try:
        if _database_exists(server, config.name):
            logger.info(
                "Database %r already exists; reconciling schema", config.name
            )
            try:
                db_conn = mysql.connector.connect(
                    **config.to_connection_args(),
                    autocommit=True,
                    connection_timeout=6,
                )
                try:
                    schema_path = _find_schema_file(config.name)
                    if schema_path:
                        migration = _reconcile_schema(db_conn, schema_path)
                        result.update(migration)
                        logger.info(
                            "Schema reconciliation: tables_created=%s "
                            "columns_added=%s",
                            migration["tables_created"],
                            migration["columns_added"],
                        )
                    _apply_safe_seeds(db_conn)
                    result["admin_present"] = _ensure_admin(db_conn)
                finally:
                    db_conn.close()
            except (mysql.connector.Error, BootstrapError) as e:
                logger.warning(
                    "Schema reconciliation skipped for existing database %r: %s",
                    config.name, e,
                )
            return result

        logger.info("Creating missing database %r", config.name)
        _create_database(server, config.name)
        result["database_created"] = True

        schema_path = _find_schema_file(config.name)
        if schema_path is None:
            schema_name = _SCHEMA_FILES.get(
                config.name, _SCHEMA_FILES["pos_system"]
            )
            raise BootstrapError(
                f"The database schema file ({schema_name}) was not found.",
                instructions=GENERIC_ERROR.format(
                    detail=f"{schema_name} could not be located next to the "
                    "application. Reinstall the application."
                ),
            )

        db_conn = mysql.connector.connect(
            **config.to_connection_args(),
            autocommit=True,
            connection_timeout=6,
        )
        try:
            _import_schema(db_conn, schema_path)
            result["schema_imported"] = True
            result["admin_present"] = _ensure_admin(db_conn)
        except Exception:
            db_conn.close()
            _drop_database(server, config.name)
            raise
        finally:
            try:
                db_conn.close()
            except Exception:
                pass
        logger.info(
            "Database %r prepared: created=%s imported=%s admin=%s",
            config.name,
            result["database_created"],
            result["schema_imported"],
            result["admin_present"],
        )
        return result
    finally:
        try:
            server.close()
        except Exception:
            pass
