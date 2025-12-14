.PHONY: fmt lint typecheck test all

fmt:
	uv run ruff format kraft tests

lint:
	uv run ruff check kraft tests

typecheck:
	uv run mypy kraft

test:
	uv run pytest

all: fmt lint typecheck test
