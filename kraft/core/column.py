"""Column definition primitives used throughout Kraft."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class ColumnDefinition:
    """Declarative metadata describing the shape of a table column.

    Each column is defined once, typically when bootstrapping a schema or
    registering a reusable column generator.  The generator callable is expected
    to return a Python value that psycopg2 can send to PostgreSQL.

    Attributes:
        name: The column identifier as it should appear in SQL.
        sql_type: PostgreSQL type literal (e.g. ``UUID`` or ``TEXT``).
        generator: Zero-arg callable that produces the next synthetic value.
        constraints: Optional constraint fragment such as ``PRIMARY KEY`` or
            ``DEFAULT now()``; appended verbatim to the DDL.
        reserved: When ``True`` the column exists in the registry but is not
            materialized in the initial schema—useful for staged rollouts.
        protected: When ``True`` the column cannot be dropped by schema
            evolution routines (e.g. primary keys or audit columns).
    """

    name: str
    sql_type: str
    generator: Callable[[], Any]
    constraints: Optional[str] = None
    reserved: bool = False
    protected: bool = False

    def generate(self) -> Any:
        """Return a fresh synthetic value for this column."""
        return self.generator()

    def ddl(self) -> str:
        """Render the column definition for CREATE/ALTER TABLE statements."""
        parts = [self.name, self.sql_type]
        if self.constraints:
            parts.append(self.constraints.strip())
        return " ".join(parts)
