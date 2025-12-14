from unittest.mock import MagicMock

from kraft.core.column import ColumnDefinition
from kraft.core.runner import SimulationRunner


def _schema_manager_with_columns():
    manager = MagicMock()
    manager.get_active_columns.return_value = {
        "id": ColumnDefinition("id", "UUID", lambda: "id"),
        "name": ColumnDefinition("name", "TEXT", lambda: "Alice"),
    }
    return manager


def test_simulation_runner_processes_batches():
    schema_manager = _schema_manager_with_columns()
    mutator = MagicMock()
    mutator.insert_batch.return_value = ["1", "2", "3", "4"]

    runner = SimulationRunner(
        schema_manager=schema_manager,
        mutator=mutator,
        total_records=4,
        batch_size=2,
    )

    runner.run()

    assert mutator.insert_batch.call_count == 2
    assert mutator.maybe_mutate_batch.call_count == 2


def test_simulation_runner_handles_zero_records():
    schema_manager = _schema_manager_with_columns()
    mutator = MagicMock()

    runner = SimulationRunner(
        schema_manager=schema_manager,
        mutator=mutator,
        total_records=0,
        batch_size=500,
    )

    runner.run()
    mutator.insert_batch.assert_not_called()
    mutator.maybe_mutate_batch.assert_not_called()


def test_simulation_runner_triggers_evolution():
    schema_manager = _schema_manager_with_columns()
    mutator = MagicMock()
    mutator.insert_batch.return_value = ["1", "2"]

    evolution = MagicMock()
    evolution.evolve.side_effect = [None, "Dropped column: name"]

    runner = SimulationRunner(
        schema_manager=schema_manager,
        mutator=mutator,
        evolution_controller=evolution,
        total_records=4,
        batch_size=2,
    )

    runner.run()
    assert evolution.evolve.call_count == 2
