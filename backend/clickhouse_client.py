from settings import HOST, CLICKHOUSE_PORT, CLICKHOUSE_USERNAME, CLICKHOUSE_PASSWORD
import clickhouse_connect
import structlog

logger = structlog.get_logger(__name__)

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

logger.info("Successfully connected to ClickHouse.")


def table_exists(table_name: str, schema_name: str) -> bool:
    query = f"SELECT name FROM system.tables WHERE database = '{schema_name}' AND name = '{table_name}'"

    try:
        result = client.command(query)
        if result and result == table_name:
            logger.info(f"Table {table_name} exists in schema {schema_name}.")
            return True
        else:
            logger.info(
                f"Table {table_name} does not exist in schema {schema_name}.")
            return False
    except Exception as e:
        logger.error(f"Error while checking table existence: {str(e)}")
        raise
