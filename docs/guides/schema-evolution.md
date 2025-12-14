# Guide: Controlling Schema Evolution

Kraft's evolution tooling is designed to emulate staged rollouts: dormant
columns become active, and low-value columns may be dropped (unless protected).

## Reserved vs Protected

- **Reserved** columns exist in metadata but do not start in the physical table.
  They are candidates for future `ALTER TABLE ... ADD COLUMN`.
- **Protected** columns (primary keys, audit columns) are never dropped even if
  an evolution cycle requests it.

## Evolution Controller Settings

| Setting | Description |
| ------- | ----------- |
| `evolution_interval` | Number of batches between evolution attempts. |
| `evolution_probability` | Chance that evolution occurs when the interval hits. |
| `add_probability` | Probability of adding versus dropping when both are allowed. |
| `max_additions` / `max_drops` | Hard safety caps. |

## Tombstoning Drops

`EvolutionController` tracks `dropped_columns` so columns cannot be re-added
accidentally. You can inspect the log via `controller.summary()` and persist it
in your own monitoring system if desired.

## Custom Strategies

If you need deterministic sequences (e.g., always add column `discount` before
`coupon`), subclass `EvolutionController` and override `_choose_action()` or
`_add_column()`/`_drop_column()` to honor bespoke rules.

```python
class PriorityEvolution(EvolutionController):
    priority = ["discount", "coupon"]

    def _add_column(self):
        for name in self.priority:
            if name in self.manager.columns and name not in self.manager.get_active_columns():
                self.manager.register_column(name, self.manager.columns[name])
        return super()._add_column()
```

In practice you can also call `SchemaManager.add_column()` manually between
simulation batches to simulate manual migrations or blue/green deployments.

## Logging

Evolution decisions are logged via the `kraft.core.evolution` logger. Raise the
log level if you want a quieter experience:

```python
import logging

logging.getLogger("kraft").setLevel(logging.WARNING)
```
