import pytest
from unittest.mock import patch, MagicMock
from data.GenerateRow import RowGenerator

column_data = [
    {"generator": "increment", "params": {}, "dataType": "int"},
    {"generator": "random", "params": {}, "dataType": "string"},
    {"generator": "email", "params": {}, "dataType": "string"},
    {"generator": "date", "params": {}, "dataType": "string"},
    {"generator": "datetime", "params": {}, "dataType": "string"},
    {"generator": "fixed", "params": {}, "dataType": "string"},
    {"generator": "range", "params": {}, "dataType": "string"},
    {"generator": "dictionary", "params": {}, "dataType": "string"},
]

config_data = {"rows": 5, "columns": column_data}


@patch("data.GenerateRow.generate_incremental_field")
@patch("data.GenerateRow.generate_random_value")
@patch("data.GenerateRow.generate_random_email")
@patch("data.GenerateRow.generate_random_date")
@patch("data.GenerateRow.generate_iso8601_date")
@patch("data.GenerateRow.return_default_value")
@patch("data.GenerateRow.generate_random_number_from_range")
@patch("data.GenerateRow.generate_random_dictionary_value")
def test_generate_row(
    mock_generate_random_dictionary_value,
    mock_generate_random_number_from_range,
    mock_return_default_value,
    mock_generate_iso8601_date,
    mock_generate_random_date,
    mock_generate_random_email,
    mock_generate_random_value,
    mock_generate_incremental_field,
):
    # We set up the mock functions to return specific values
    mock_generate_incremental_field.return_value = 1
    mock_generate_random_value.return_value = "test"
    mock_generate_random_email.return_value = "email@test.com"
    mock_generate_random_date.return_value = "2023-01-01"
    mock_generate_iso8601_date.return_value = "2023-01-01T12:34:56"
    mock_return_default_value.return_value = "default"
    mock_generate_random_number_from_range.return_value = 5
    mock_generate_random_dictionary_value.return_value = "random_dict_value"

    row_generator = RowGenerator(config_data)
    row = row_generator.generate_row(1, column_data)

    # Assert the function calls and their order
    mock_generate_incremental_field.assert_called_once_with(1, {}, "int")
    mock_generate_random_value.assert_called_once_with(1, {}, "string")
    mock_generate_random_email.assert_called_once_with(1, {}, "string")
    mock_generate_random_date.assert_called_once_with(1, {}, "string")
    mock_generate_iso8601_date.assert_called_once_with(1, {}, "string")
    mock_return_default_value.assert_called_once_with(1, {}, "string")
    mock_generate_random_number_from_range.assert_called_once_with(
        1, {}, "string")
    mock_generate_random_dictionary_value.assert_called_once_with(
        1, {}, "string")

    # Assert the result
    assert row == [
        1,
        "test",
        "email@test.com",
        "2023-01-01",
        "2023-01-01T12:34:56",
        "default",
        5,
        "random_dict_value",
    ]
