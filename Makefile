.PHONY: fmt lint typecheck test all

fmt:
	uv run ruff format kroft tests

lint:
	uv run ruff check kroft tests

typecheck:
	uv run mypy kroft

test:
	uv run pytest

all: fmt lint typecheck test
