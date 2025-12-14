from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ColumnDefinition:
    """Declarative metadata describing a table column."""

    name: str
    sql_type: str
    generator: Callable[[], Any]
    constraints: str | None = None
    reserved: bool = False
    protected: bool = False

    def generate(self) -> Any:
        """Return a new synthetic value for this column."""
        return self.generator()

    def ddl(self) -> str:
        """Render the column definition for CREATE/ALTER TABLE statements."""
        parts = [self.name, self.sql_type]
        if self.constraints:
            parts.append(self.constraints.strip())
        return " ".join(parts)
