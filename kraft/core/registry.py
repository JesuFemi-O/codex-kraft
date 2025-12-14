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
    return _REGISTRY.copy()


def clear_column_registry() -> None:
    _REGISTRY.clear()
