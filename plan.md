# Kroft Library Strategic Plan

This document scopes what is required to turn the Kroft codebase into a production-quality, PyPI-ready package. It captures product goals, functional and non-functional requirements, repository expectations, and the concrete work streams needed to get there.

## 1. Problem Definition

- **Goal**: Provide a reusable library for simulating high-volume CDC workloads (insert/update/delete streams) while continuously evolving database schemas in a controlled, testable manner.
- **Primary Users**: Data engineers and platform teams validating ingestion pipelines, CDC consumers, or schema evolution tooling without touching production data.
- **Value Prop**: Easily define column registries, materialize schemas, generate synthetic batches, mutate rows, and orchestrate automated schema evolution against PostgreSQL targets.

## 2. Minimum Viable Feature Set

1. **Schema Modeling**
   - Declarative column definition API (types, generators, constraints, reserved/protected flags).
   - Schema manager that can create/drop tables, promote reserved columns, and guard protected columns.
   - Registry/decorator utilities for sharing column definitions across simulations.
2. **Data Generation & Mutation**
   - Batch generator that respects column metadata (reserved/protected) and supports registry-backed schemas.
   - Mutation engine for bulk insertions plus probabilistic updates/deletes with automatic `updated_at` maintenance when configured.
3. **Schema Evolution Control**
   - Evolution controller with configurable cadence/probabilities for column promotion/dropping.
   - Audit trail of schema changes (adds/drops) and tombstoning of dropped columns to prevent re-addition without opt-in overrides.
4. **Simulation Runner**
   - High-level runner tying schema manager, batch generator, mutation engine, and evolution controller together.
   - Hooks for custom mutation/evolution strategies.

## 3. Non-Functional Requirements

- **Packaging**: Standard `pyproject.toml` with accurate dependencies (e.g., `psycopg2-binary`), classifiers, license, and optional extras (`dev`, `examples`).
- **Python Versions**: 3.10+ with CI testing matrix (3.10, 3.11, 3.12).
- **Code Quality**: Ruff (lint & format), type checking (Pyright or Mypy), 100% pytest coverage on critical modules. Guard rails on random behavior via seeding hooks.
- **Documentation**: Rich README + API reference (Sphinx or mkdocs) and tutorial notebooks showing registry usage and schema evolution scenarios.
- **Examples**: Reusable scripts leveraging Dockerized PostgreSQL so users can run end-to-end simulations locally or in CI.
- **Security & Stability**: No raw SQL string interpolation; rely on `psycopg2.sql` helpers. Clear error handling/messages around schema mismatches.

## 4. Repository Structure

```
kroft/
  __init__.py
  core/
    column.py
    schema.py
    batch.py
    mutator.py
    evolution.py
    runner.py
  registry/
    __init__.py
    decorators.py
docs/
  index.md
  api/
examples/
  basic_simulation.py
  registry_simulation.py
tests/
  core/
  integration/
  e2e/
pyproject.toml
README.md
CONTRIBUTING.md
CHANGELOG.md
```

## 5. Work Streams & Tasks

### 5.1 Packaging & Tooling
- Flesh out `pyproject.toml` metadata (description, authors, license, URLs).
- Move runtime dependencies from `requirements.txt` into `[project.dependencies]`; keep `requirements-dev.txt` for tooling when necessary.
- Add `ruff` configuration covering lint + format rules; introduce type checker config.
- Introduce `make` or `uv` tasks for `lint`, `test`, `typecheck`, `fmt`.

### 5.2 Core API Hardening
- Enforce presence/validation of `update_column` when schema includes a timestamp column; automatically protect that column from drops.
- Refactor `SimulationRunner` to only use public APIs (`SchemaManager.get_active_columns`, `MutationEngine.maybe_mutate_batch`).
- Track dropped columns in `SchemaManager` (e.g., `self.dropped_columns` set) and block re-addition unless explicitly requested.
- Provide structured evolution history objects consumable by downstream dashboards.

### 5.3 Testing & QA
- Expand unit tests to cover edge cases (no generator, custom PK types, concurrent evolution).
- Add integration tests using a temporary PostgreSQL (Docker + pytest fixture) that run schema creation, batch insertion, mutation, and evolution end-to-end.
- Capture coverage reports in CI to prevent regressions.

### 5.4 Documentation & Examples
- Rewrite README with quickstart, architecture diagram, API summary, and links to docs.
- Provide cookbook-style examples (basic simulation, registry-driven, custom evolution).
- Document extension points (custom generators, external mutation policies).

### 5.5 CI/CD
- GitHub Actions workflow that:
  1. Runs Ruff lint + format check.
  2. Runs type checker.
  3. Spins up PostgreSQL service, runs integration tests.
  4. Uploads coverage artifacts.
  5. On tagged releases, builds sdist/wheel and publishes to PyPI using trusted publishing.
- Cache dependencies (`actions/setup-python` + uv cache) for faster builds.

### 5.6 Release Management
- Semantic versioning with changelog automation (e.g., `towncrier`).
- Pre-release validation script ensuring migrations/tests/docs all pass.
- PyPI metadata validation via `twine check`.

## 6. Success Criteria

- Library installable via `pip install kroft`, usable with minimal setup, and documented.
- CI green across supported Python versions with integration tests proving real Postgres behavior.
- Clear contributor guide and automated checks that prevent regressions.
- Schema evolution audit trail and column protection semantics align with CDC best practices.

By executing the work streams above, the Kroft project will transition from an experimental code dump to a polished, trustworthy package ready for open-source adoption and PyPI distribution.
