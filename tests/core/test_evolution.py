from unittest.mock import MagicMock, patch

from kraft.core.column import ColumnDefinition
from kraft.core.evolution import EvolutionController
from kraft.core.schema import SchemaManager


def _make_schema_manager():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor

    columns = {
        "id": ColumnDefinition("id", "UUID", lambda: "1", protected=True),
        "name": ColumnDefinition("name", "TEXT", lambda: "Alice"),
        "age": ColumnDefinition("age", "INT", lambda: 30, reserved=True),
        "email": ColumnDefinition("email", "TEXT", lambda: "a@b.com", reserved=True),
    }
    manager = SchemaManager(conn, schema="public", table_name="people", columns=columns)
    return manager


@patch("kraft.core.evolution.random.random", return_value=0.0)
@patch("kraft.core.evolution.random.choice", side_effect=lambda seq: seq[0])
def test_evolution_controller_adds_then_drops(mock_choice, mock_random):
    manager = _make_schema_manager()
    controller = EvolutionController(
        manager,
        evolution_interval=1,
        evolution_probability=1.0,
        add_probability=1.0,
        max_additions=2,
        max_drops=1,
    )

    msg1 = controller.evolve(batch_number=1)
    assert msg1.startswith("[v2] Added column")
    assert controller.num_additions == 1

    msg2 = controller.evolve(batch_number=2)
    assert msg2.startswith("[v3] Added column")
    assert controller.num_additions == 2

    controller.add_probability = 0.0  # force drop
    msg3 = controller.evolve(batch_number=3)
    assert msg3.startswith("[v4] Dropped column")
    assert controller.num_drops == 1

    msg4 = controller.evolve(batch_number=4)
    assert msg4 == "No evolution possible"
    assert controller.summary()["adds"] == 2
    assert controller.summary()["drops"] == 1


def test_evolution_controller_respects_interval():
    manager = _make_schema_manager()
    controller = EvolutionController(
        manager,
        evolution_interval=3,
        evolution_probability=1.0,
    )

    assert controller.evolve(batch_number=1) is None
    assert controller.evolve(batch_number=2) is None
