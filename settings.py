import os
import logging
import structlog
from dotenv import load_dotenv

load_dotenv()


USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

# Agency ID
AGENCY_ID = int(os.getenv('AGENCY_ID'))

# ClickHouse Configuration
HOST = os.getenv('CLICKHOUSE_HOST')
CLICKHOUSE_PORT = os.getenv('CLICKHOUSE_PORT')
CLICKHOUSE_USERNAME = os.getenv('CLICKHOUSE_USERNAME')
CLICKHOUSE_PASSWORD = os.getenv('CLICKHOUSE_PASSWORD')
SCHEMA_NAME = "im_8730_031"


def configure_structlog():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# Call the function
configure_structlog()
