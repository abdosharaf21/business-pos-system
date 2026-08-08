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

    def execute(self, sql, params=None):
        self.last_execute = sql
        self.executed_statements.append(sql)

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
