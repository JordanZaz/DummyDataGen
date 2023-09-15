import pytest
from unittest.mock import Mock, patch
import backend.clickhouse_client as clickhouseClient


def test_table_exists():
    # Create mock objects for table_name and schema_name
    table_name = "test_table_name"
    schema_name = "test_schema_name"

    # This function will be used to replace the original client.command function during the test
    def mock_command(query):
        # We assume that the query is correctly formatted and simply check if the table_name is in it
        if table_name in query:
            return table_name  # Simulate a case where the table exists
        else:
            return []  # Simulate a case where the table does not exist

    # Use the patch function to replace client.command with mock_command during the test
    with patch("backend.clickhouse_client.client.command", new=mock_command):
        # Call the function being tested with the table existing
        result = clickhouseClient.table_exists(table_name, schema_name)
        # Assert that the result is True, as we are simulating that the table exists
        assert result == True

        # Call the function being tested with the table not existing
        result = clickhouseClient.table_exists(
            "non_existent_table", schema_name)
        # Assert that the result is False, as we are simulating that the table does not exist
        assert result == False
