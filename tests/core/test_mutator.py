from unittest.mock import MagicMock, patch

from kraft.core.batch import BatchGenerator
from kraft.core.column import ColumnDefinition
from kraft.core.mutator import MutationEngine


def _mock_conn():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn, cursor


@patch("kraft.core.mutator.execute_values")
def test_insert_batch_persists_rows(mock_execute_values):
    conn, cursor = _mock_conn()
    engine = MutationEngine(
        conn,
        schema="public",
        table_name="events",
        primary_key="id",
    )

    rows = [
        {"id": "1", "value": 10},
        {"id": "2", "value": 20},
    ]
    inserted = engine.insert_batch(rows)

    assert inserted == ["1", "2"]
    assert engine.total_inserts == 2
    mock_execute_values.assert_called_once()
    cursor.execute.assert_not_called()


@patch("kraft.core.mutator.random.random", return_value=0.4)
@patch("kraft.core.mutator.random.choice", side_effect=["update", "value"])
@patch("kraft.core.mutator.random.sample", return_value=["a"])
def test_maybe_mutate_batch_updates_when_triggered(mock_sample, mock_choice, mock_random):
    conn, _ = _mock_conn()
    schema = {
        "id": ColumnDefinition("id", "UUID", lambda: "a"),
        "value": ColumnDefinition("value", "INT", lambda: 1),
    }
    generator = BatchGenerator(schema=schema)

    engine = MutationEngine(
        conn,
        schema="public",
        table_name="events",
        primary_key="id",
        update_column="updated_at",
        generator=generator,
    )

    updated, deleted = engine.maybe_mutate_batch(["a", "b", "c", "d"])

    assert updated == 1
    assert deleted == 0
    assert engine.total_updates == 1


@patch("kraft.core.mutator.random.choice", side_effect=["delete"])
@patch("kraft.core.mutator.random.random", return_value=0.4)
@patch("kraft.core.mutator.random.sample", return_value=["b"])
def test_maybe_mutate_batch_can_delete(mock_sample, mock_random, mock_choice):
    conn, cursor = _mock_conn()
    engine = MutationEngine(conn, schema="public", table_name="events")

    updated, deleted = engine.maybe_mutate_batch(["a", "b", "c", "d"])

    assert updated == 0
    assert deleted == 1
    cursor.execute.assert_called()  # delete query executed


def test_update_records_short_circuits_without_generator():
    conn, _ = _mock_conn()
    engine = MutationEngine(conn, schema="public", table_name="events")
    assert engine._update_records(["a"]) == 0


def test_update_records_respects_modifiable_columns():
    conn, cursor = _mock_conn()
    schema = {
        "id": ColumnDefinition("id", "UUID", lambda: "a", protected=True),
        "price": ColumnDefinition("price", "FLOAT", lambda: 1.0),
        "quantity": ColumnDefinition("quantity", "INT", lambda: 1),
    }
    generator = BatchGenerator(schema=schema)
    engine = MutationEngine(
        conn,
        schema="public",
        table_name="events",
        primary_key="id",
        generator=generator,
    )

    count = engine._update_records(["1", "2"])
    assert count == 2
    assert cursor.execute.call_count == 2


def test_delete_records_handles_empty_batches():
    conn, cursor = _mock_conn()
    engine = MutationEngine(conn, schema="public", table_name="events")

    assert engine._delete_records([]) == 0
    cursor.execute.assert_not_called()


def test_delete_records_casts_uuid_array_when_needed():
    conn, cursor = _mock_conn()
    schema = {
        "id": ColumnDefinition("id", "UUID", lambda: "uuid"),
    }
    generator = BatchGenerator(schema=schema)
    engine = MutationEngine(
        conn,
        schema="public",
        table_name="events",
        primary_key="id",
        generator=generator,
    )

    engine._delete_records(["uuid-1", "uuid-2"])
    query = cursor.execute.call_args[0][0]
    assert "::uuid[]" in query


def test_get_counters_reports_totals():
    conn, _ = _mock_conn()
    engine = MutationEngine(conn, schema="public", table_name="events")
    engine.total_inserts = 5
    engine.total_updates = 3
    engine.total_deletes = 1
    assert engine.get_counters() == {
        "total_inserts": 5,
        "total_updates": 3,
        "total_deletes": 1,
    }
