from kraft.core.column import ColumnDefinition


def test_column_definition_exposes_metadata_and_generator():
    col = ColumnDefinition(
        name="price",
        sql_type="NUMERIC",
        generator=lambda: 19.99,
        constraints="NOT NULL",
        reserved=True,
        protected=True,
    )

    assert col.name == "price"
    assert col.sql_type == "NUMERIC"
    assert col.constraints == "NOT NULL"
    assert col.reserved is True
    assert col.protected is True
    assert col.generate() == 19.99


def test_column_definition_renders_valid_ddl():
    col = ColumnDefinition(
        name="created_at",
        sql_type="TIMESTAMP",
        generator=lambda: "now()",
        constraints="DEFAULT now()",
    )

    assert col.ddl() == "created_at TIMESTAMP DEFAULT now()"
