from settings import HOST, CLICKHOUSE_PORT, CLICKHOUSE_USERNAME, CLICKHOUSE_PASSWORD
import clickhouse_connect


client = clickhouse_connect.get_client(
    host=HOST,
    port=CLICKHOUSE_PORT,
    username=CLICKHOUSE_USERNAME,
    password=CLICKHOUSE_PASSWORD,
    connect_timeout=2400,
    send_receive_timeout=3600,
    query_retries=5,
    secure=False,
)


def table_exists(table_name: str, schema_name: str) -> bool:
    query = f"SELECT name FROM system.tables WHERE database = '{schema_name}' AND name = '{table_name}'"
    result = client.command(query)
    if result and result == table_name:
        return True
    return False
