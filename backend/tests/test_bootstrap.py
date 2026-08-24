"""Unit tests for database bootstrap schema parsing and reconciliation."""

import os

import pytest

from backend.database import bootstrap

_SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "db",
    "pos_system.sql",
)


class MockCursor:
    """Minimal cursor double that records executed statements."""

    def __init__(self, counts=None, columns=None):
        self._counts = list(counts or [])
        self._columns = list(columns or [])
        self.executed_statements = []
        self.last_execute = ""
        self.rowcount = 0

    def execute(self, sql, params=None):
        self.last_execute = sql
        self.executed_statements.append(sql)
        if sql.lstrip().upper().startswith("INSERT"):
            self.rowcount = 1

    def fetchone(self):
        if "information_schema.tables" in self.last_execute:
            return (self._counts.pop(0),) if self._counts else (0,)
        if "information_schema.columns" in self.last_execute:
            if self._columns:
                return self._columns.pop(0)
            return None
        return None

    def fetchall(self):
        if "information_schema.columns" in self.last_execute:
            rows = self._columns
            self._columns = []
            return rows
        return []

    def close(self):
        pass


class MockConnection:
    """Connection double that returns a single shared cursor."""

    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor


def _schema_tables():
    """Return parsed schema tables from the bundled SQL file."""
    return bootstrap._parse_create_statements(_SCHEMA_PATH)


def test_parse_create_statements_parses_all_tables():
    """The parser must discover every CREATE TABLE in the schema."""
    tables = _schema_tables()
    expected = {
        "users", "categories", "products", "customers", "suppliers",
        "sales", "sale_items", "purchases", "purchase_items",
        "expense_categories", "expenses", "inventory_transactions",
        "inventory", "stock_movements", "inventory_audits",
        "inventory_audit_items", "notifications", "store_settings",
        "refresh_token_blocklist", "warehouses", "transfers",
        "transfer_items",
        "clients", "service_categories", "services", "client_services",
        "deals",
    }
    assert set(tables.keys()) == expected


def test_parse_create_statements_identifies_columns():
    """Column names must be extracted without constraint noise."""
    purchases_columns = {
        column for column, _ in _schema_tables()["purchases"]["columns"]
    }
    assert {
        "id", "supplier_id", "user_id", "invoice_number", "total_amount",
        "status", "payment_method", "notes", "created_at",
    }.issubset(purchases_columns)
    assert not {"REFERENCES", "ON", "CONSTRAINT", "INDEX"} & purchases_columns


def test_parse_create_statements_keeps_full_create_sql():
    """The raw CREATE TABLE statement must include ENGINE and COLLATE."""
    create_sql = _schema_tables()["users"]["create_sql"]
    assert create_sql.startswith("CREATE TABLE IF NOT EXISTS users")
    assert create_sql.rstrip().endswith(";")
    assert "ENGINE=InnoDB" in create_sql
    assert "COLLATE=utf8mb4_unicode_ci" in create_sql


def test_reconcile_schema_creates_missing_tables_and_adds_columns(monkeypatch):
    """Reconciliation must create missing tables and add missing columns."""
    tables = _schema_tables()
    cursor = MockCursor()
    conn = MockConnection(cursor)

    monkeypatch.setattr(bootstrap, "_table_exists", lambda conn, name: name == "products")
    monkeypatch.setattr(
        bootstrap,
        "_existing_columns",
        lambda conn, name: {"id", "name"} if name == "products" else set(),
    )

    result = bootstrap._reconcile_schema(conn, _SCHEMA_PATH)

    assert result["tables_created"] == len(tables) - 1
    assert result["columns_added"] > 0
    assert any(
        stmt.startswith("CREATE TABLE IF NOT EXISTS")
        for stmt in cursor.executed_statements
    )
    assert any(stmt.startswith("ALTER TABLE") for stmt in cursor.executed_statements)


def test_reconcile_schema_is_noop_when_synced(monkeypatch):
    """A fully migrated database must result in no changes."""
    tables = _schema_tables()
    cursor = MockCursor()
    conn = MockConnection(cursor)

    monkeypatch.setattr(
        bootstrap, "_table_exists", lambda conn, name: name in tables
    )
    monkeypatch.setattr(
        bootstrap,
        "_existing_columns",
        lambda conn, name: {
            column for column, _ in tables[name]["columns"]
        },
    )

    result = bootstrap._reconcile_schema(conn, _SCHEMA_PATH)

    assert result == {"tables_created": 0, "columns_added": 0}
    assert cursor.executed_statements == []


def test_table_exists_queries_information_schema(monkeypatch):
    """_table_exists must query information_schema.tables."""
    cursor = MockCursor(counts=[1])
    conn = MockConnection(cursor)

    assert bootstrap._table_exists(conn, "users") is True
    assert "information_schema.tables" in cursor.last_execute


def test_existing_columns_returns_column_names(monkeypatch):
    """_existing_columns must return the set of existing column names."""
    cursor = MockCursor(columns=[("id",), ("name",)])
    conn = MockConnection(cursor)

    assert bootstrap._existing_columns(conn, "products") == {"id", "name"}
    assert "information_schema.columns" in cursor.last_execute


def _run_reconcile(monkeypatch, cursor, indexes=None, not_null=None):
    """Run _reconcile_warehouse_model with information_schema doubles."""
    monkeypatch.setattr(
        bootstrap,
        "_index_exists",
        lambda conn, table, name: name in (indexes or set()),
    )
    monkeypatch.setattr(
        bootstrap,
        "_column_is_not_null",
        lambda conn, table, column: column in (not_null or set()),
    )
    conn = MockConnection(cursor)
    return bootstrap._reconcile_warehouse_model(conn)


def test_reconcile_warehouse_model_full_upgrade(monkeypatch):
    """Legacy DB: seeds warehouses, backfills stock, swaps unique key."""
    cursor = MockCursor()
    result = _run_reconcile(
        monkeypatch,
        cursor,
        indexes={bootstrap.LEGACY_INVENTORY_UNIQUE_KEY},
        not_null={"category_id"},
    )

    assert result["warehouses_seeded"] is True
    assert result["inventory_backfilled"] >= 0
    assert result["unique_key_swapped"] is True
    assert result["category_nullable_fixed"] is True

    executed = [stmt for stmt in cursor.executed_statements]
    assert any("INSERT INTO warehouses" in stmt for stmt in executed)
    add_key_at = next(
        i for i, stmt in enumerate(executed) if "ADD UNIQUE KEY" in stmt
    )
    drop_key_at = next(
        i for i, stmt in enumerate(executed) if "DROP INDEX" in stmt
    )
    assert add_key_at < drop_key_at
    assert any(
        "MODIFY COLUMN category_id INT NULL" in stmt for stmt in executed
    )


def test_reconcile_warehouse_model_is_noop_when_migrated(monkeypatch):
    """A database already on the warehouse model must not be altered."""
    cursor = MockCursor()
    result = _run_reconcile(
        monkeypatch,
        cursor,
        indexes={bootstrap.NEW_INVENTORY_UNIQUE_KEY},
        not_null=set(),
    )

    assert result["unique_key_swapped"] is False
    assert result["category_nullable_fixed"] is False
    executed = cursor.executed_statements
    assert not any("ADD UNIQUE KEY" in stmt for stmt in executed)
    assert not any("DROP INDEX" in stmt for stmt in executed)
    assert not any("MODIFY COLUMN" in stmt for stmt in executed)


def test_reconcile_warehouse_model_seeds_use_duplicate_guard(monkeypatch):
    """Warehouse seeding must be idempotent via ON DUPLICATE KEY."""
    cursor = MockCursor()
    result = _run_reconcile(
        monkeypatch,
        cursor,
        indexes={bootstrap.LEGACY_INVENTORY_UNIQUE_KEY},
        not_null=set(),
    )

    seed_stmt = next(
        stmt for stmt in cursor.executed_statements
        if "INSERT INTO warehouses" in stmt
    )
    assert "ON DUPLICATE KEY UPDATE id = id" in seed_stmt
    assert isinstance(result["warehouses_seeded"], bool)
