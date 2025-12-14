# Getting Started

## Installation

```bash
git clone https://github.com/<your-org>/kraft.git
cd kraft
uv sync  # or python -m venv .venv && pip install -e .[dev]
```

## Running Tests

```bash
uv run pytest             # unit tests
uv run pytest -m integration  # requires KRAFT_TEST_PG_DSN
```

For integration tests and examples, start Postgres via `docker compose up -d postgres` and export:

```bash
export KRAFT_TEST_PG_DSN="dbname=kraft_test user=postgres password=postgres host=localhost port=55432"
export KRAFT_EXAMPLE_DSN="$KRAFT_TEST_PG_DSN"
```

## Examples

```bash
uv run python examples/basic_simulation.py
uv run python examples/registry_simulation.py
```

Both use the `KRAFT_EXAMPLE_DSN` connection string.
