# Architecture

Kraft is intentionally modular so you can reuse individual building blocks or run
the entire simulation loop. The diagram below describes how the modules
collaborate during a typical batch:

1. **SchemaManager** materializes the physical schema and exposes the set of
   active columns.
2. **BatchGenerator** reads those definitions to emit a batch of synthetic rows.
3. **MutationEngine** writes the batch and may mutate a subset of records.
4. **EvolutionController** decides whether a reserved column should be promoted
   or an unprotected column dropped.
5. **SimulationRunner** orchestrates the loop, ensuring the generator always
   reflects the latest schema state.

```
SchemaManager ---> BatchGenerator ---> MutationEngine
       ^                                    |
       |                                    v
EvolutionController <--- SimulationRunner (control loop)
```

## Design Principles

- **Deterministic contracts** – Every module has a narrow, well-documented
  surface area with predictable side effects.
- **Extensibility** – You can swap components (e.g., custom evolution logic) as
  long as you honor the corresponding interfaces.
- **Observability** – Components track counters and provide structured summaries
  so simulations can feed dashboards or acceptance tests.

## Schema Lifecycle

The lifecycle of a column typically follows these states:

1. **Registered** – Defined via decorator or direct dictionary entry.
2. **Active** – Materialized in the table and available to the batch generator.
3. **Dropped** – Removed from the table (unless protected) and recorded in the
   evolution controller's log to prevent accidental re-addition.

Protected columns (primary keys, ``updated_at``, etc.) skip step 3 to safeguard
critical invariants.
