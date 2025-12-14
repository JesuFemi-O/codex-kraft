from __future__ import annotations

from collections.abc import Callable

from kraft.core.column import ColumnDefinition

_REGISTRY: dict[str, ColumnDefinition] = {}


def register_column(
    *,
    name: str,
    sql_type: str,
    constraints: str | None = None,
    reserved: bool = False,
    protected: bool = False,
) -> Callable[[Callable[[], object]], Callable[[], object]]:
    """Decorator that records a callable as a reusable column generator."""

    def decorator(func: Callable[[], object]) -> Callable[[], object]:
        _REGISTRY[name] = ColumnDefinition(
            name=name,
            sql_type=sql_type,
            generator=func,
            constraints=constraints,
            reserved=reserved,
            protected=protected,
        )
        return func

    return decorator


def get_registered_columns() -> dict[str, ColumnDefinition]:
    """Return a copy of the current registry."""
    return _REGISTRY.copy()


def clear_column_registry() -> None:
    """Test helper to reset the registry between runs."""
    _REGISTRY.clear()
