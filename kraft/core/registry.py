"""Global column registry with decorator-based ergonomics."""

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
    """Register a reusable column generator via decorator syntax.

    Example:
        >>> @register_column(name="sku", sql_type="TEXT")
        ... def sku():
        ...     return secrets.token_hex(4)

    Args:
        name: Registry key and SQL column name.
        sql_type: PostgreSQL type literal.
        constraints: Optional constraint snippet appended to DDL.
        reserved: Whether the column should start inactive.
        protected: Whether the column may be dropped.
    """

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
    """Remove all registered columns (useful for tests/examples)."""
    _REGISTRY.clear()
