from kraft.core.column import ColumnDefinition


def test_column_definition_exposes_metadata_and_generator():
    column = ColumnDefinition(
        name="price",
        sql_type="NUMERIC",
        generator=lambda: 9.99,
        constraints="NOT NULL",
        reserved=True,
        protected=True,
    )

    assert column.name == "price"
    assert column.sql_type == "NUMERIC"
    assert column.constraints == "NOT NULL"
    assert column.reserved is True
    assert column.protected is True
    assert column.generate() == 9.99


def test_column_definition_renders_valid_ddl():
    col = ColumnDefinition(
        name="created_at",
        sql_type="TIMESTAMP",
        generator=lambda: "now()",
        constraints="DEFAULT now()",
    )

    assert col.ddl() == "created_at TIMESTAMP DEFAULT now()"
