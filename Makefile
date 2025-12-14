.PHONY: fmt lint typecheck test integration docs all

fmt:
	uv run ruff format kraft tests

lint:
	uv run ruff check kraft tests

typecheck:
	uv run mypy kraft

test:
	uv run pytest

integration:
	uv run pytest tests/integration -m integration

docs:
	uv run python -m mkdocs build --strict

all: fmt lint typecheck test
