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
