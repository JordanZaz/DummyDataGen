import pytest
from data.yml_to_clickhouse import YMLtoClickhouse


def test_print_create_table():
    table_name = "test_table"
    columns = [
        {"name": "column1", "dataType": "int", "generator": "increment"},
        {"name": "column2", "dataType": "string", "generator": "random"},
    ]

    yml_to_ck = YMLtoClickhouse()

    expected_result = (
        "CREATE TABLE im_8730_031.test_table (\n"
        "  column1 Int32 DEFAULT rowNumberInAllBlocks(),\n"
        "  column2 String,\n"
        "  PRIMARY KEY (column1)\n"
        ") ENGINE = MergeTree ORDER BY (column1, column2);\n\n"
    )
    assert yml_to_ck.generate_create_table(
        table_name, columns) == expected_result


def test_print_create_table_invalid_increment():
    table_name = "test_table"
    columns = [
        {"name": "column1", "dataType": "string", "generator": "increment"}]

    yml_to_ck = YMLtoClickhouse()

    with pytest.raises(ValueError) as excinfo:
        yml_to_ck.generate_create_table(table_name, columns)
    assert "The 'increment' generator can only be applied to 'int' columns." in str(
        excinfo.value
    )


def test_print_insert_row():
    table_name = "test_table"
    rows = [[1, "random1"], [2, "random2"]]
    columns = [
        {
            "name": "column1",
            "dataType": "int",
            "generator": "increment",
            "params": {"start": 1, "step": 1},
        },
        {"name": "column2", "dataType": "string", "generator": "random"},
    ]

    yml_to_ck = YMLtoClickhouse()

    expected_result = (
        "INSERT INTO im_8730_031.test_table (column1, column2) VALUES "
        "(1, 'random1'), "
        "(2, 'random2');"
    )
    assert yml_to_ck.generate_insert_row(
        table_name, rows, columns, 2) == expected_result
