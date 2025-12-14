# Guide: Running Simulations

This guide walks through composing the core primitives to run an end-to-end
simulation targeting a PostgreSQL database.

## 1. Define Columns

Use either inline dictionaries or the decorator-based registry:

```python
from kraft import ColumnDefinition

columns = {
    "id": ColumnDefinition("id", "UUID", lambda: uuid.uuid4().hex, protected=True),
    "updated_at": ColumnDefinition("updated_at", "TIMESTAMP", lambda: "now()", protected=True),
    "sku": ColumnDefinition("sku", "TEXT", lambda: random.choice(PRODUCTS)),
    "qty": ColumnDefinition("qty", "INT", lambda: random.randint(1, 5)),
    "discount": ColumnDefinition("discount", "FLOAT", lambda: 0.0, reserved=True),
}
```

## 2. Create Schema Manager

```python
manager = SchemaManager(conn, schema="public", table_name="sales", columns=columns)
manager.drop_table()
manager.create_table()
```

## 3. Wire Generator, Mutator, and Evolution Controller

```python
generator = BatchGenerator(schema=manager.get_active_columns())
mutator = MutationEngine(
    conn,
    schema="public",
    table_name="sales",
    primary_key="id",
    update_column="updated_at",
    generator=generator,
)
evolution = EvolutionController(
    manager,
    evolution_interval=5,
    evolution_probability=0.6,
    add_probability=0.7,
    max_additions=3,
    max_drops=1,
)
```

## 4. Run the Simulation

```python
runner = SimulationRunner(
    schema_manager=manager,
    mutator=mutator,
    batch_generator=generator,
    evolution_controller=evolution,
    total_records=1000,
    batch_size=50,
)
runner.run()
```

Inspect counters to verify workload characteristics:

```python
print(mutator.get_counters())
print(evolution.summary())
```

## Controlling Logging

The Kraft modules log `INFO`-level events (inserts, drops, evolution decisions).
If you prefer a quieter console, raise the level before starting your runner:

```python
import logging

logging.basicConfig(level=logging.WARNING)
# or only mute Kraft:
logging.getLogger("kraft").setLevel(logging.WARNING)
```

## Tips

- Adjust ``batch_size`` to match the throughput you need to test.
- Override ``MutationEngine.maybe_mutate_batch`` or wrap it if you want to force
  deterministic mutation ratios.
- Use the registry example in ``examples/registry_simulation.py`` when multiple
  simulations need to share a baseline schema.
