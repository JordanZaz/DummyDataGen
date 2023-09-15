import pytest
import sqlite3
from unittest.mock import Mock, patch
from backend.generate_json import generate_table_meta


def test_generate_table_meta():
    # Create mock objects for user_id, datasource, report_type, and table_name
    user_id = "test_user"
    datasource = "test_datasource"
    report_type = "test_report_type"
    table_name = "test_table_name"

    # This function will be used to replace the original get_connection function
    # during the test
    def mock_get_connection():
        # Create a mock connection object
        mock_conn = Mock(spec=sqlite3.Connection)

        # Create a mock cursor object
        mock_cursor = Mock(spec=sqlite3.Cursor)

        # Set up the mock cursor's fetchall method to return some dummy data
        mock_cursor.fetchall.return_value = [
            {"field_sql_name": "test_field", "field_data_type": "int"}
        ]

        # Set up the mock connection's cursor method to return the mock cursor
        mock_conn.cursor.return_value = mock_cursor

        return mock_conn

    # Use the patch function to replace get_connection with mock_get_connection
    # during the test
    with patch("backend.generate_json.get_connection", new=mock_get_connection):
        # Call the function being tested
        result = generate_table_meta(
            user_id, datasource, report_type, table_name)

    # Assert that the result is as expected
    assert result == {
        "columns": [
            {
                "name": "test_field",
                "dataType": "string",
                "generator": "random",
                "params": {"length": 10},
            }
        ],
        "tableName": table_name,
    }
