from __future__ import annotations

import random
from typing import Dict, Iterable, List, Optional, Tuple

from psycopg2 import sql
from psycopg2.extras import execute_values

from kraft.core.batch import BatchGenerator


class MutationEngine:
    """Perform bulk insert/update/delete operations against a PostgreSQL table."""

    def __init__(
        self,
        conn,
        *,
        schema: str,
        table_name: str,
        primary_key: str = "id",
        update_column: Optional[str] = None,
        generator: Optional[BatchGenerator] = None,
    ):
        self.conn = conn
        self.schema = schema
        self.table_name = table_name
        self.primary_key = primary_key
        self.update_column = update_column
        self.generator = generator

        self.total_inserts = 0
        self.total_updates = 0
        self.total_deletes = 0

    def insert_batch(self, rows: List[Dict[str, object]]) -> List[object]:
        if not rows:
            return []

        columns = list(rows[0].keys())
        inserted_ids = [row[self.primary_key] for row in rows]

        query = sql.SQL("INSERT INTO {}.{} ({}) VALUES %s").format(
            sql.Identifier(self.schema),
            sql.Identifier(self.table_name),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
        )
        values = [[row[col] for col in columns] for row in rows]
        with self.conn.cursor() as cur:
            execute_values(cur, query, values)
            self.conn.commit()

        self.total_inserts += len(rows)
        return inserted_ids

    def maybe_mutate_batch(self, ids: Iterable[object]) -> Tuple[int, int]:
        ids = list(ids)
        if not ids or random.random() > 0.5:
            return 0, 0

        operation = random.choice(["update", "delete"])
        sample_size = max(1, len(ids) // 4)
        subset = random.sample(ids, sample_size)

        if operation == "update":
            updated = self._update_records(subset)
            self.total_updates += updated
            return updated, 0
        deleted = self._delete_records(subset)
        self.total_deletes += deleted
        return 0, deleted

    def _update_records(self, ids: List[object]) -> int:
        if not ids or not self.generator:
            return 0

        modifiable = self.generator.get_modifiable_columns(exclude=[self.primary_key])
        if not modifiable:
            return 0

        with self.conn.cursor() as cur:
            for row_id in ids:
                column = random.choice(modifiable)
                value = self.generator.generate_value(column)

                if self.update_column:
                    query = sql.SQL(
                        "UPDATE {}.{} SET {} = %s, {} = now() WHERE {} = %s"
                    ).format(
                        sql.Identifier(self.schema),
                        sql.Identifier(self.table_name),
                        sql.Identifier(column),
                        sql.Identifier(self.update_column),
                        sql.Identifier(self.primary_key),
                    )
                    cur.execute(query, (value, row_id))
                else:
                    query = sql.SQL("UPDATE {}.{} SET {} = %s WHERE {} = %s").format(
                        sql.Identifier(self.schema),
                        sql.Identifier(self.table_name),
                        sql.Identifier(column),
                        sql.Identifier(self.primary_key),
                    )
                    cur.execute(query, (value, row_id))
            self.conn.commit()

        return len(ids)

    def _delete_records(self, ids: List[object]) -> int:
        if not ids:
            return 0

        pk_type = self._primary_key_type()
        cast = "::uuid[]" if pk_type == "UUID" else ""
        query = (
            f'DELETE FROM "{self.schema}"."{self.table_name}" '
            f'WHERE "{self.primary_key}" = ANY(%s{cast});'
        )
        with self.conn.cursor() as cur:
            cur.execute(query, (ids,))
            self.conn.commit()

        return len(ids)

    def _primary_key_type(self) -> str:
        if self.generator and self.primary_key in self.generator.schema:
            return self.generator.schema[self.primary_key].sql_type.upper()
        return "TEXT"

    def get_counters(self) -> Dict[str, int]:
        return {
            "total_inserts": self.total_inserts,
            "total_updates": self.total_updates,
            "total_deletes": self.total_deletes,
        }
