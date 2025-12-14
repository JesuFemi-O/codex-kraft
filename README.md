# Kraft

Synthetic CDC simulator and schema evolution toolkit for PostgreSQL.

See `plan.md` and `tasks.md` for the current roadmap.

## Integration Tests

To run the PostgreSQL integration suite:

1. Start a Postgres instance locally (example with Docker Compose):
   ```bash
   docker compose up -d postgres
   ```
   or with `docker run`:
   ```bash
   docker run --rm -p 55432:5432 \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=kraft_test \
     postgres:16
   ```
2. Export a DSN for the tests:
   ```bash
   export KRAFT_TEST_PG_DSN="dbname=kraft_test user=postgres password=postgres host=localhost port=55432"
   ```
3. Run the integration tests:
   ```bash
   uv run pytest tests/integration -m integration
   ```

Without the `KRAFT_TEST_PG_DSN` variable the integration tests are automatically skipped.

## Examples

Two runnable examples live in `examples/`:

1. **Basic simulation** (`examples/basic_simulation.py`) – Inlines a schema definition, runs a short simulation loop with mutations and schema evolution.
2. **Registry simulation** (`examples/registry_simulation.py`) – Demonstrates the column registry decorator API and shared columns.

Both require a PostgreSQL DSN exported as `KRAFT_EXAMPLE_DSN` (same connection string as the integration tests). Run them with:

```bash
export KRAFT_EXAMPLE_DSN="dbname=kraft_test user=postgres password=postgres host=localhost port=55432"
uv run python examples/basic_simulation.py
uv run python examples/registry_simulation.py
```

## Documentation & CI

- Build docs locally with `make docs` (runs `mkdocs build --strict`).
- Serve with `uv run python -m mkdocs serve` for live reload while authoring.
- `Kraft CI` workflow runs linting, type checking, unit/integration tests, and a docs smoke build on every push/PR.
- `Docs Site` workflow deploys the docs to GitHub Pages from `main`.

## Logging Control

Kraft’s core modules emit `INFO` logs (e.g., inserts, schema changes). To silence them globally in your app:

```python
import logging

logging.basicConfig(level=logging.WARNING)
# or target Kraft specifically:
logging.getLogger("kraft").setLevel(logging.WARNING)
```
