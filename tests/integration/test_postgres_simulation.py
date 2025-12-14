import os
import uuid
from typing import Dict

import psycopg2
import pytest

from kraft import (
    BatchGenerator,
    ColumnDefinition,
    EvolutionController,
    MutationEngine,
    SchemaManager,
    SimulationRunner,
)

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def pg_conn():
    dsn = os.getenv("KRAFT_TEST_PG_DSN")
    if not dsn:
        pytest.skip("Set KRAFT_TEST_PG_DSN to run PostgreSQL integration tests.")
    conn = psycopg2.connect(dsn)
    yield conn
    conn.close()


def _integration_columns() -> Dict[str, ColumnDefinition]:
    return {
        "id": ColumnDefinition("id", "UUID", lambda: str(uuid.uuid4())),
        "updated_at": ColumnDefinition(
            "updated_at",
            "TIMESTAMP",
            lambda: "now()",
            protected=True,
        ),
        "item": ColumnDefinition("item", "TEXT", lambda: "widget"),
        "quantity": ColumnDefinition("quantity", "INT", lambda: 1),
        "discount": ColumnDefinition("discount", "FLOAT", lambda: 0.0, reserved=True),
    }


def test_full_simulation_flow(pg_conn):
    table = "integration_sales"
    columns = _integration_columns()
    manager = SchemaManager(pg_conn, schema="public", table_name=table, columns=columns)

    manager.drop_table()
    manager.create_table()

    generator = BatchGenerator(schema=manager.get_active_columns())
    mutator = MutationEngine(
        pg_conn,
        schema="public",
        table_name=table,
        primary_key="id",
        update_column="updated_at",
        generator=generator,
    )
    evolution = EvolutionController(
        manager,
        evolution_interval=2,
        evolution_probability=1.0,
        add_probability=1.0,
        max_additions=1,
        max_drops=0,
    )
    runner = SimulationRunner(
        schema_manager=manager,
        mutator=mutator,
        batch_generator=generator,
        evolution_controller=evolution,
        total_records=6,
        batch_size=2,
    )

    runner.run()

    with pg_conn.cursor() as cur:
        cur.execute(f'SELECT count(*) FROM public."{table}";')
        row_count = cur.fetchone()[0]

    counters = mutator.get_counters()
    assert row_count == counters["total_inserts"] - counters["total_deletes"]
    assert counters["total_inserts"] >= 6
    summary = evolution.summary()
    assert summary["adds"] >= 1

    manager.drop_table()
