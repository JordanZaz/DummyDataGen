from typing import Any, Dict, List, Generator
from .generator_functions import *
import structlog

logger = structlog.get_logger(__name__)


class RowGenerator:
    def __init__(self, configuration: Dict[str, Any]):
        self.configuration = configuration
        self.generators = {
            "increment": generate_incremental_field,
            "random": generate_random_value,
            "email": generate_random_email,
            "date": generate_random_date,
            "datetime": generate_iso8601_date,
            "fixed": return_default_value,
            "range": generate_random_number_from_range,
            "dictionary": generate_random_dictionary_value,
        }

    def generate_row(self, index: int, columns: List[Dict[str, Any]]) -> List[str]:
        fields: List[str] = []
        for column in columns:
            generator_name = column.get("generator", "default")
            generator_func = self.generators.get(generator_name)

            if not generator_func:
                raise ValueError(f"Unknown generator: {generator_name}")

            params = column.get("params", {})
            dataType = column.get("dataType", "")

            fields.append(generator_func(index, params, dataType))
        return fields

    def generate_data(self) -> Generator[List[str], None, None]:
        # Default to 1000 if "rows" not specified
        rows = self.configuration.get("rows")
        columns = self.configuration.get("columns", [])

        # Iterate through the rows and columns to generate the data
        for row_num in range(rows):
            yield self.generate_row(row_num, columns)
        logger.info("Completed generating rows",
                    total_rows=rows, total_columns=len(columns))
