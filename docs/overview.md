# Overview

Kraft is a synthetic CDC simulator and schema evolution toolkit. It helps you:

- Model schemas with reserved/protected columns that evolve over time.
- Generate synthetic batches, mutate records, and observe change streams.
- Stress-test CDC ingestion or downstream systems without using production data.

## Core Components

- **ColumnDefinition** – declarative column metadata including generators and constraints.
- **SchemaManager** – applies DDL, tracks active/reserved columns, and versions schema state.
- **BatchGenerator** – produces synthetic rows from column definitions or the registry.
- **MutationEngine** – handles inserts, updates, and deletes with timestamp updates.
- **EvolutionController** – decides when to add/drop columns and logs changes.
- **SimulationRunner** – orchestrates the full flow end-to-end.

## Roadmap & Docs

See `plan.md` and `tasks.md` in the repository for ongoing work. Use this documentation site for user guides and API reference.
