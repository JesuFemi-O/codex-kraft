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


def test_register_column_decorator_populates_registry():
    @register_column(name="id", sql_type="UUID", protected=True)
    def id_gen():
        return "mock-id"

    registered = get_registered_columns()
    assert set(registered) == {"id"}

    col = registered["id"]
    assert col.name == "id"
    assert col.sql_type == "UUID"
    assert col.protected is True
    assert col.generate() == "mock-id"


def test_register_column_honors_constraints_and_reserved_flags():
    @register_column(
        name="discount",
        sql_type="FLOAT",
        constraints="DEFAULT 0.0",
        reserved=True,
    )
    def discount_gen():
        return 0.0

    col = get_registered_columns()["discount"]
    assert col.constraints == "DEFAULT 0.0"
    assert col.reserved is True
    assert col.ddl() == "discount FLOAT DEFAULT 0.0"
