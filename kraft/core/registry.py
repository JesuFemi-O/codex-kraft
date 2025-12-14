from __future__ import annotations

from typing import Callable, Dict, Optional

from kraft.core.column import ColumnDefinition

_REGISTRY: Dict[str, ColumnDefinition] = {}


def register_column(
    *,
    name: str,
    sql_type: str,
    constraints: Optional[str] = None,
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


def get_registered_columns() -> Dict[str, ColumnDefinition]:
    """Return a copy of the current registry."""
    return _REGISTRY.copy()


def clear_column_registry() -> None:
    """Test helper to reset the registry between runs."""
    _REGISTRY.clear()
