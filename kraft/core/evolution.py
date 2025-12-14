"""Decision engine that orchestrates schema evolution events."""

from __future__ import annotations

import logging
import random

from kraft.core.schema import SchemaManager

logger = logging.getLogger(__name__)


class EvolutionController:
    """Decide when and how to evolve the active schema."""

    def __init__(
        self,
        manager: SchemaManager,
        *,
        evolution_interval: int = 25,
        evolution_probability: float = 0.2,
        add_probability: float = 0.7,
        max_additions: int = 10,
        max_drops: int = 5,
    ):
        """
        Args:
            manager: :class:`SchemaManager` instance to mutate.
            evolution_interval: Number of batches between evolution attempts.
            evolution_probability: Chance that an evolution will run when the
                interval elapses.
            add_probability: Likelihood that an evolution attempt performs an
                ADD vs DROP when both are allowed.
            max_additions: Upper bound on how many columns may be added.
            max_drops: Upper bound on how many columns may be dropped.
        """
        self.manager = manager
        self.evolution_interval = evolution_interval
        self.evolution_probability = evolution_probability
        self.add_probability = add_probability
        self.max_additions = max_additions
        self.max_drops = max_drops

        self.num_additions = 0
        self.num_drops = 0
        self.evolution_log: list[dict[str, str]] = []
        self.dropped_columns: set[str] = set()

    def should_evolve(self, batch_number: int) -> bool:
        """Return ``True`` if the controller should attempt evolution."""
        if batch_number % self.evolution_interval != 0:
            return False
        return random.random() < self.evolution_probability

    def evolve(self, batch_number: int) -> str | None:
        if not self.should_evolve(batch_number):
            return None

        action = self._choose_action()
        if action == "add":
            result = self._add_column()
        elif action == "drop":
            result = self._drop_column()
        else:
            result = None

        if result:
            self.evolution_log.append(result)
            logger.info("%s", result["message"])
        return result["message"] if result else "No evolution possible"

    def _choose_action(self) -> str:
        can_add = self.num_additions < self.max_additions and self._has_available_columns()
        can_drop = self.num_drops < self.max_drops and self._has_droppable_columns()

        if can_add and not can_drop:
            return "add"
        if can_drop and not can_add:
            return "drop"
        if not can_add and not can_drop:
            return "none"

        return "add" if random.random() < self.add_probability else "drop"

    def _has_available_columns(self) -> bool:
        return any(
            col.reserved
            and name not in self.manager.get_active_columns()
            and name not in self.dropped_columns
            for name, col in self.manager.columns.items()
        )

    def _has_droppable_columns(self) -> bool:
        return any(not col.protected for col in self.manager.get_active_columns().values())

    def _add_column(self) -> dict[str, str] | None:
        promoted = self.manager.add_column()
        if not promoted:
            return None

        self.num_additions += 1
        return {
            "version": f"v{self.manager.schema_version}",
            "action": "add",
            "column": promoted,
            "message": f"[v{self.manager.schema_version}] Added column: {promoted}",
        }

    def _drop_column(self) -> dict[str, str] | None:
        dropped = self.manager.drop_column()
        if not dropped:
            return None

        self.num_drops += 1
        self.dropped_columns.add(dropped)
        return {
            "version": f"v{self.manager.schema_version}",
            "action": "drop",
            "column": dropped,
            "message": f"[v{self.manager.schema_version}] Dropped column: {dropped}",
        }

    def summary(self) -> dict[str, object]:
        return {
            "schema_version": self.manager.schema_version,
            "adds": self.num_additions,
            "drops": self.num_drops,
            "max_adds": self.max_additions,
            "max_drops": self.max_drops,
            "log": self.evolution_log,
            "dropped_columns": sorted(self.dropped_columns),
        }
