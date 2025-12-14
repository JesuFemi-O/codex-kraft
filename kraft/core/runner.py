"""High-level orchestrator that glues Kraft components together."""

from __future__ import annotations

from collections.abc import Iterable

from kraft.core.batch import BatchGenerator
from kraft.core.column import ColumnDefinition
from kraft.core.evolution import EvolutionController
from kraft.core.mutator import MutationEngine
from kraft.core.registry import get_registered_columns
from kraft.core.schema import SchemaManager


class SimulationRunner:
    """Coordinate batch generation, mutations, and schema evolution."""

    def __init__(
        self,
        schema_manager: SchemaManager,
        mutator: MutationEngine,
        *,
        total_records: int = 10_000,
        batch_size: int = 500,
        batch_generator: BatchGenerator | None = None,
        evolution_controller: EvolutionController | None = None,
        column_registry: dict[str, ColumnDefinition] | None = None,
        protected_columns: Iterable[str] | None = None,
    ):
        """
        Args:
            schema_manager: Manages physical table schema and evolution history.
            mutator: Performs inserts/updates/deletes for each batch.
            total_records: Total number of synthetic records to emit.
            batch_size: Number of rows generated per iteration.
            batch_generator: Optional generator instance; a new one will be
                created automatically when omitted.
            evolution_controller: Optional controller that decides when to add
                or drop columns.
            column_registry: Optional registry snapshot to seed new generators.
            protected_columns: Additional columns that should never be dropped.
        """
        self.schema_manager = schema_manager
        self.mutator = mutator
        self.total_records = total_records
        self.batch_size = batch_size
        self.batch_generator = batch_generator or BatchGenerator(
            schema=self.schema_manager.get_active_columns()
        )
        self.evolution_controller = evolution_controller
        self.column_registry = column_registry or get_registered_columns()
        self.protected_columns = set(protected_columns or [])

        self.total_batches = (
            total_records // batch_size if batch_size else 0
        )

    def run(self) -> None:
        """Execute the simulation loop."""
        if self.total_batches <= 0:
            return

        for batch_num in range(1, self.total_batches + 1):
            self.batch_generator.schema = self.schema_manager.get_active_columns()
            rows = self.batch_generator.generate_batch(self.batch_size)

            inserted_ids = self.mutator.insert_batch(rows)
            self.mutator.maybe_mutate_batch(inserted_ids)

            if self.evolution_controller:
                result = self.evolution_controller.evolve(batch_num)
                if result and "Dropped column" in result:
                    self._refresh_generator_schema()

    def _refresh_generator_schema(self) -> None:
        """Point the batch generator at the latest active column set."""
        self.batch_generator.schema = self.schema_manager.get_active_columns()
