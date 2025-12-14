from unittest.mock import patch

import pytest

from kraft.core.batch import BatchGenerator
from kraft.core.column import ColumnDefinition


def test_batch_generator_requires_schema_or_registry():
    with pytest.raises(ValueError):
        BatchGenerator()


@patch("kraft.core.batch.get_registered_columns", return_value={})
def test_batch_generator_can_pull_from_registry(mock_registry):
    generator = BatchGenerator(use_registry=True)

    assert generator.schema == {}
    mock_registry.assert_called_once_with()


def test_batch_generator_validates_schema_entries():
    with pytest.raises(TypeError):
        BatchGenerator(schema={"foo": "bar"})  # type: ignore[arg-type]


def test_generate_batch_produces_expected_rows():
    schema = {
        "id": ColumnDefinition("id", "UUID", lambda: "123"),
        "name": ColumnDefinition("name", "TEXT", lambda: "Alice"),
    }
    generator = BatchGenerator(schema=schema)

    rows = generator.generate_batch(batch_size=2)
    assert rows == [
        {"id": "123", "name": "Alice"},
        {"id": "123", "name": "Alice"},
    ]


def test_generate_value_for_known_column():
    generator = BatchGenerator(
        schema={"value": ColumnDefinition("value", "INT", lambda: 42)}
    )
    assert generator.generate_value("value") == 42
    with pytest.raises(KeyError):
        generator.generate_value("missing")


def test_get_modifiable_columns_skips_reserved_protected_and_excluded():
    schema = {
        "id": ColumnDefinition("id", "UUID", lambda: "1", protected=True),
        "flag": ColumnDefinition("flag", "BOOLEAN", lambda: True, reserved=True),
        "price": ColumnDefinition("price", "FLOAT", lambda: 1.23),
        "quantity": ColumnDefinition("quantity", "INT", lambda: 5),
    }
    generator = BatchGenerator(schema=schema)
    assert set(generator.get_modifiable_columns(exclude=["quantity"])) == {"price"}
