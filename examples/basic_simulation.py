"""Basic Kraft simulation example.

Run with:
    export KRAFT_EXAMPLE_DSN="dbname=kraft_test user=postgres password=postgres host=localhost port=55432"
    uv run python examples/basic_simulation.py
"""

import os
import random
import uuid

import psycopg2

from kraft import (
    BatchGenerator,
    ColumnDefinition,
    EvolutionController,
    MutationEngine,
    SchemaManager,
    SimulationRunner,
)

TABLE_NAME = "example_sales"


def build_columns():
    return {
        "id": ColumnDefinition("id", "UUID", lambda: str(uuid.uuid4()), protected=True),
        "updated_at": ColumnDefinition(
            "updated_at", "TIMESTAMP", lambda: "now()", protected=True
        ),
        "item": ColumnDefinition(
            "item", "TEXT", lambda: random.choice(["shoes", "shirt", "hat"])
        ),
        "region": ColumnDefinition(
            "region", "TEXT", lambda: random.choice(["NA", "EU", "APAC"])
        ),
        "quantity": ColumnDefinition("quantity", "INT", lambda: random.randint(1, 5)),
        "discount": ColumnDefinition("discount", "FLOAT", lambda: 0.0, reserved=True),
        "coupon": ColumnDefinition("coupon", "TEXT", lambda: "NONE", reserved=True),
    }


def run_simulation(conn):
    columns = build_columns()
    manager = SchemaManager(conn, schema="public", table_name=TABLE_NAME, columns=columns)
    manager.drop_table()
    manager.create_table()

    generator = BatchGenerator(schema=manager.get_active_columns())
    mutator = MutationEngine(
        conn,
        schema="public",
        table_name=TABLE_NAME,
        primary_key="id",
        update_column="updated_at",
        generator=generator,
    )
    evolution = EvolutionController(
        manager,
        evolution_interval=3,
        evolution_probability=0.8,
        add_probability=0.7,
        max_additions=2,
        max_drops=1,
    )
    runner = SimulationRunner(
        schema_manager=manager,
        mutator=mutator,
        batch_generator=generator,
        evolution_controller=evolution,
        total_records=30,
        batch_size=5,
    )

    runner.run()
    print("Mutation stats:", mutator.get_counters())
    print("Evolution summary:", evolution.summary())


def main():
    dsn = os.getenv("KRAFT_EXAMPLE_DSN")
    if not dsn:
        raise SystemExit(
            "Set KRAFT_EXAMPLE_DSN to a psycopg2 connection string before running."
        )
    with psycopg2.connect(dsn) as conn:
        run_simulation(conn)


if __name__ == "__main__":
    main()
