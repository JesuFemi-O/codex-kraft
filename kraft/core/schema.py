"""High-level schema management helpers."""

from __future__ import annotations

import logging
from typing import Any

from kraft.core.column import ColumnDefinition

logger = logging.getLogger(__name__)


class SchemaManager:
    """Create, drop, and evolve a table schema from declarative column metadata."""

    def __init__(
        self,
        conn: Any,
        *,
        schema: str,
        table_name: str,
        columns: dict[str, ColumnDefinition],
    ):
        """
        Args:
            conn: psycopg2 connection object with privileges to run DDL.
            schema: Database schema (namespace) for the managed table.
            table_name: Target table name.
            columns: Mapping of column name to definition including reserved or
                protected flags.
        """
        self.conn = conn
        self.schema = schema
        self.table_name = table_name
        self.columns = columns

        self.active_columns: dict[str, ColumnDefinition] = {
            name: col for name, col in columns.items() if not col.reserved
        }
        self.schema_version = 1
        self.schema_history: list[set[str]] = [set(self.active_columns)]

    # ------------------------------------------------------------------ #
    #   Table lifecycle helpers                                          #
    # ------------------------------------------------------------------ #
    def get_active_columns(self) -> dict[str, ColumnDefinition]:
        return self.active_columns

    def get_create_table_sql(self) -> str:
        """Render the SQL used by :meth:`create_table`."""
        body = ",\n  ".join(col.ddl() for col in self.active_columns.values())
        return (
            f"CREATE TABLE IF NOT EXISTS {self.schema}.{self.table_name} (\n"
            f"  {body}\n"
            ");"
        )

    def create_table(self) -> None:
        """Execute ``CREATE TABLE IF NOT EXISTS`` using the active columns."""
        logger.info("Ensuring table %s.%s exists", self.schema, self.table_name)
        with self.conn.cursor() as cur:
            cur.execute(self.get_create_table_sql())
            self.conn.commit()

    def drop_table(self) -> None:
        """Drop the managed table if it exists."""
        ddl = f"DROP TABLE IF EXISTS {self.schema}.{self.table_name};"
        logger.info("Dropping table %s.%s if it exists", self.schema, self.table_name)
        with self.conn.cursor() as cur:
            cur.execute(ddl)
            self.conn.commit()

    # ------------------------------------------------------------------ #
    #   Schema evolution helpers                                         #
    # ------------------------------------------------------------------ #
    def add_column(self) -> str | None:
        candidates = [
            name
            for name, col in self.columns.items()
            if col.reserved and name not in self.active_columns
        ]
        if not candidates:
            return None

        chosen = candidates[0]
        definition = self.columns[chosen]
        ddl = (
            f"ALTER TABLE {self.schema}.{self.table_name} "
            f"ADD COLUMN {definition.ddl()};"
        )
        logger.info("Adding reserved column '%s' to %s.%s", chosen, self.schema, self.table_name)
        with self.conn.cursor() as cur:
            cur.execute(ddl)
            self.conn.commit()

        self.active_columns[chosen] = definition
        self._bump_version()
        return chosen

    def drop_column(self) -> str | None:
        candidates = [
            name
            for name, col in self.active_columns.items()
            if not col.protected
        ]
        if not candidates:
            return None

        chosen = candidates[0]
        ddl = (
            f"ALTER TABLE {self.schema}.{self.table_name} "
            f"DROP COLUMN {chosen};"
        )
        logger.warning("Dropping column '%s' from %s.%s", chosen, self.schema, self.table_name)
        with self.conn.cursor() as cur:
            cur.execute(ddl)
            self.conn.commit()

        del self.active_columns[chosen]
        self._bump_version()
        return chosen

    def register_column(self, name: str, definition: ColumnDefinition) -> bool:
        """Add a brand new column definition to the registry."""
        if name in self.columns:
            return False
        self.columns[name] = definition
        if not definition.reserved:
            self.active_columns[name] = definition
            self._bump_version()
        return True

    def _bump_version(self) -> None:
        """Increment the schema version and record the active column set."""
        self.schema_version += 1
        self.schema_history.append(set(self.active_columns))
