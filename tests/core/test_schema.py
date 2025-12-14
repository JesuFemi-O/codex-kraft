from unittest.mock import MagicMock

from kraft.core.column import ColumnDefinition
from kraft.core.schema import SchemaManager


def _mock_conn():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn, cursor


def test_create_table_uses_active_columns_only():
    conn, cursor = _mock_conn()
    columns = {
        "id": ColumnDefinition("id", "UUID", lambda: "id", protected=True),
        "payload": ColumnDefinition("payload", "JSONB", lambda: {}),
        "new_col": ColumnDefinition("new_col", "TEXT", lambda: "x", reserved=True),
    }

    manager = SchemaManager(conn, schema="public", table_name="events", columns=columns)

    manager.create_table()
    cursor.execute.assert_called_once()
    sql = cursor.execute.call_args[0][0]
    assert "new_col" not in sql  # reserved column excluded
    assert "payload" in sql


def test_add_column_promotes_reserved_column():
    conn, cursor = _mock_conn()
    columns = {
        "id": ColumnDefinition("id", "UUID", lambda: "id"),
        "reserved": ColumnDefinition("reserved", "TEXT", lambda: "x", reserved=True),
    }
    manager = SchemaManager(conn, schema="public", table_name="events", columns=columns)

    added = manager.add_column()
    assert added == "reserved"
    cursor.execute.assert_called_once()
    assert "ADD COLUMN reserved TEXT" in cursor.execute.call_args[0][0]
    assert "reserved" in manager.get_active_columns()


def test_drop_column_skips_protected_columns():
    conn, cursor = _mock_conn()
    columns = {
        "id": ColumnDefinition("id", "UUID", lambda: "id", protected=True),
        "value": ColumnDefinition("value", "INT", lambda: 1),
    }
    manager = SchemaManager(conn, schema="public", table_name="events", columns=columns)

    dropped = manager.drop_column()
    assert dropped == "value"
    cursor.execute.assert_called_once()
    assert "DROP COLUMN value" in cursor.execute.call_args[0][0]


def test_register_column_adds_to_active_when_not_reserved():
    conn, _ = _mock_conn()
    columns = {
        "id": ColumnDefinition("id", "UUID", lambda: "id"),
    }
    manager = SchemaManager(conn, schema="public", table_name="events", columns=columns)

    success = manager.register_column(
        "new_col",
        ColumnDefinition("new_col", "TEXT", lambda: "hi"),
    )

    assert success is True
    assert "new_col" in manager.get_active_columns()
    assert manager.schema_version == 2

