"""Registry-driven example that reuses column definitions across simulations."""

import os
import random
import uuid

import psycopg2

from kraft import (
    BatchGenerator,
    EvolutionController,
    MutationEngine,
    SchemaManager,
    SimulationRunner,
    clear_column_registry,
    get_registered_columns,
    register_column,
)

TABLE_NAME = "registry_sales"


def register_columns():
    clear_column_registry()

    @register_column(name="id", sql_type="UUID", protected=True)
    def generate_id():
        return str(uuid.uuid4())

    @register_column(name="updated_at", sql_type="TIMESTAMP", protected=True)
    def updated_at():
        return "now()"

    @register_column(name="product", sql_type="TEXT")
    def product():
        return random.choice(["bag", "jacket", "socks"])

    @register_column(name="quantity", sql_type="INT")
    def quantity():
        return random.randint(1, 10)

    @register_column(name="unit_price", sql_type="FLOAT")
    def unit_price():
        return round(random.uniform(15, 120), 2)

    @register_column(name="discount_rate", sql_type="FLOAT", reserved=True)
    def discount():
        return 0.0

    @register_column(name="coupon_code", sql_type="TEXT", reserved=True)
    def coupon():
        return random.choice(["NONE", "SUMMER", "VIP"])


def run_simulation(conn):
    register_columns()
    columns = get_registered_columns()
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
        evolution_interval=2,
        evolution_probability=1.0,
        add_probability=1.0,
        max_additions=2,
        max_drops=0,
    )

    runner = SimulationRunner(
        schema_manager=manager,
        mutator=mutator,
        batch_generator=generator,
        evolution_controller=evolution,
        total_records=20,
        batch_size=4,
    )
    runner.run()

    print("Registry simulation stats:")
    print("Mutation:", mutator.get_counters())
    print("Evolution:", evolution.summary())


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
