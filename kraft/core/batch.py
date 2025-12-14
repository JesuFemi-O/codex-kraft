"""Utilities for generating batches of synthetic rows."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from kraft.core.column import ColumnDefinition
from kraft.core.registry import get_registered_columns


class BatchGenerator:
    """Generate dictionaries that resemble table rows.

    The generator can build from a supplied ``schema`` mapping or lazily load
    from the global column registry.  Schemas are mutable so tests and runners
    can swap in an updated set of active columns between batches.
    """

    def __init__(
        self,
        schema: dict[str, ColumnDefinition] | None = None,
        *,
        use_registry: bool = False,
    ):
        """
        Args:
            schema: Mapping of column name to :class:`ColumnDefinition`.  If
                omitted you can set ``use_registry`` to load from the global
                decorator registry instead.
            use_registry: When ``True`` the generator clones all registered
                columns and uses them as the backing schema.
        """
        if schema is not None:
            self.schema = schema
        elif use_registry:
            self.schema = get_registered_columns()
        else:
            raise ValueError("Must supply a schema or set use_registry=True")

        self._validate_schema()

    def _validate_schema(self) -> None:
        """Ensure the provided schema only contains :class:`ColumnDefinition` entries."""
        if not isinstance(self.schema, dict):
            raise TypeError("Schema must be a mapping of ColumnDefinition objects.")
        for name, column in self.schema.items():
            if not isinstance(column, ColumnDefinition):
                raise TypeError(f"Schema entry '{name}' is not a ColumnDefinition.")

    def generate_value(self, column: str) -> Any:
        """Generate a single value for the given column name."""
        if column not in self.schema:
            raise KeyError(f"Unknown column '{column}'")
        return self.schema[column].generate()

    def generate_batch(self, batch_size: int) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for _ in range(batch_size):
            row = {name: col.generate() for name, col in self.schema.items()}
            rows.append(row)
        return rows

    def get_modifiable_columns(self, *, exclude: Iterable[str] | None = None) -> list[str]:
        excluded = set(exclude or [])
        return [
            name
            for name, column in self.schema.items()
            if not column.reserved and not column.protected and name not in excluded
        ]
