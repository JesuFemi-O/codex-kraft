import pytest

from kraft.core.registry import (
    clear_column_registry,
    get_registered_columns,
    register_column,
)


@pytest.fixture(autouse=True)
def reset_registry():
    clear_column_registry()
    yield
    clear_column_registry()


def test_register_column_populates_registry_snapshot():
    @register_column(name="id", sql_type="UUID", protected=True)
    def id_gen():
        return "uuid-1"

    registered = get_registered_columns()
    assert list(registered) == ["id"]

    col = registered["id"]
    assert col.protected is True
    assert col.generate() == "uuid-1"


def test_register_column_supports_constraints_and_reserved():
    @register_column(
        name="discount",
        sql_type="FLOAT",
        constraints="DEFAULT 0.0",
        reserved=True,
    )
    def discount_gen():
        return 0.0

    col = get_registered_columns()["discount"]
    assert col.reserved is True
    assert col.ddl() == "discount FLOAT DEFAULT 0.0"
