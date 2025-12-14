# Kroft Work Breakdown

This task list mirrors the plan while keeping units small enough for review/push cycles. Each block should be tackled in order; after your approval we continue with the next block.

## Phase 0 – Repo Bootstrapping
1. **Initialize project structure**
   - Create `kroft/` package skeleton, `tests/`, `examples/`, `docs/` placeholder, `pyproject.toml`, `README.md`, `LICENSE`, `.gitignore`.
   - Add `plan.md`, `tasks.md`, and basic `CONTRIBUTING.md`.
2. **Set up tooling scaffolding**
   - Configure Ruff (lint + format), type checker (Pyright/Mypy), pytest settings.
   - Add `makefile`/`uv` scripts for `lint`, `fmt`, `test`, `typecheck`.

## Phase 1 – Core API Foundations
3. **Column & Registry API**
   - Implement `ColumnDefinition`, registry decorators, and initial unit tests.
4. **Schema Manager MVP**
   - Add table creation/drop, active vs reserved columns, column protection logic.
   - Write tests using `MagicMock` DB connection.

## Phase 2 – Data Generation & Mutation
5. **Batch Generator**
   - Implement schema-driven batch creation + modifiable column selection.
   - Add tests covering reserved/protected logic.
6. **Mutation Engine**
   - Insert/update/delete paths with timestamp awareness.
   - Unit tests using mock connections and seeded randomness.

## Phase 3 – Evolution & Runner
7. **Evolution Controller**
   - Add evolution scheduling, logging, tombstoning for dropped columns.
   - Tests to confirm add/drop limits and audit log behavior.
8. **Simulation Runner**
   - Wire SchemaManager + BatchGenerator + MutationEngine + EvolutionController.
   - Ensure only public APIs are used; add unit tests (mocks).

## Phase 4 – Integration & Examples
9. **Postgres integration tests**
   - Docker-based fixture or local test harness to exercise create → mutate → evolve flow.
10. **Example scripts/notebooks**
    - Basic simulation + registry-driven example, updated to newest APIs.

## Phase 5 – Documentation & Site
11. **Docs tooling**
    - Choose MkDocs/MkDocs-Material, set up `mkdocs.yml`, `docs/` structure, API reference via `mkdocstrings`.
12. **Content & GitHub Pages**
    - Write tutorials, architecture overview, API docs; configure Pages deployment workflow.

## Phase 6 – CI/CD & Release Prep
13. **CI pipelines**
    - GitHub Actions workflow for lint, typecheck, tests (unit + integration), docs build, coverage upload.
14. **Release automation**
    - Trusted publishing setup, changelog automation (e.g., Towncrier), PyPI publishing workflow.

We can pause after any task for your review/merge before moving on. Let me know where you’d like to start.***
