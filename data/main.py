import yaml
import structlog
from typing import List, Tuple
from settings import SCHEMA_NAME

from .generate_row import RowGenerator
from .yml_to_clickhouse import YMLtoClickhouse

logger = structlog.get_logger(__name__)


class DataGenerator:
    def __init__(self, yaml_string: str, schema_name=SCHEMA_NAME):
        logger.info("Initializing DataGenerator", schema_name=schema_name)
        try:
            self.data = yaml.safe_load(yaml_string)
        except yaml.YAMLError as exc:
            logger.error("Error loading YAML", error=exc)
            self.data = {}
        self.row_gen = RowGenerator(self.data)
        self.ymlToClickhouse = YMLtoClickhouse(schema_name)

    def generate_data(self) -> List[List[str]]:
        rows = list(self.row_gen.generate_data())
        for row in rows:
            if len(row) != len(self.data["columns"]):
                raise ValueError(
                    "Number of values in row doesn't match the number of columns."
                )
        return rows

    def create_table_statement(self) -> str:
        return self.ymlToClickhouse.generate_create_table(
            self.data["tableName"], self.data["columns"]
        )

    def insert_row_statements(self, rows: List[List[str]]) -> str:
        return self.ymlToClickhouse.generate_insert_row(
            self.data["tableName"], rows, self.data["columns"]
        )

    def generate_sql_queries(self) -> str:
        logger.info("Generating SQL queries")
        rows = self.generate_data()
        return self.create_table_statement() + self.insert_row_statements(rows)


def generate_data_from_yaml(
    yaml_string: str, schema_name=SCHEMA_NAME
) -> Tuple[str, List[str]]:
    logger.info("Generating data from YAML", schema_name=schema_name)
    data_gen = DataGenerator(yaml_string, schema_name)
    rows = data_gen.generate_data()
    return data_gen.create_table_statement(), data_gen.insert_row_statements(rows)


def generate_query_from_yaml(yaml_string: str, schema_name=SCHEMA_NAME) -> str:
    logger.info("Generating query from YAML", schema_name=schema_name)
    data_gen = DataGenerator(yaml_string, schema_name)
    return data_gen.generate_sql_queries()
