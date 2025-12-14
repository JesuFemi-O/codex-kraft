from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from kraft.core.column import ColumnDefinition
from kraft.core.registry import get_registered_columns


class BatchGenerator:
    """Generate synthetic rows from column definitions."""

    def __init__(
        self,
        schema: dict[str, ColumnDefinition] | None = None,
        *,
        use_registry: bool = False,
    ):
        if schema is not None:
            self.schema = schema
        elif use_registry:
            self.schema = get_registered_columns()
        else:
            raise ValueError("Must supply a schema or set use_registry=True")

        self._validate_schema()

    def _validate_schema(self) -> None:
        if not isinstance(self.schema, dict):
            raise TypeError("Schema must be a mapping of ColumnDefinition objects.")
        for name, column in self.schema.items():
            if not isinstance(column, ColumnDefinition):
                raise TypeError(f"Schema entry '{name}' is not a ColumnDefinition.")

    def generate_value(self, column: str) -> Any:
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
