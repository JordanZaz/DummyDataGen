from settings import SCHEMA_NAME
import datetime
from typing import Dict, Any, List, Union
import structlog

logger = structlog.get_logger(__name__)


class YMLtoClickhouse:
    def __init__(self, schema_name=SCHEMA_NAME):
        self.schema_name = schema_name
        self.data_types = {
            "int": "Int32",
            "float": "Float",
            "float64": "Decimal64(2)",
            "boolean": "Bool",
            "string": "String",
            "date": "Date",
            "datetime": "DateTime",
            "decimal32(2)": "Decimal32(2)",
            "decimal64(2)": "Decimal64(2)",
        }

    def generate_create_table(
        self, table_name: str, columns: List[Dict[str, Union[str, bool]]]
    ) -> str:
        logger.info("Creating table", table_name=table_name, columns=columns)
        create_table_statement = f"CREATE TABLE {self.schema_name}.{table_name} (\n"
        primary_key = ""
        order_by_column = ""
        for column in columns:
            data_type = self.data_types[column["dataType"]]
            create_table_statement += f"  {column['name']} {data_type}"
            if column["generator"] == "increment":
                if column["dataType"] != "int":
                    raise ValueError(
                        f"The 'increment' generator can only be applied to 'int' columns. Column '{column['name']}' has dataType '{column['dataType']}'."
                    )
                create_table_statement += " DEFAULT rowNumberInAllBlocks()"
                primary_key = column["name"]
            create_table_statement += ",\n"

            if column.get("orderBy", False):
                order_by_column = column["name"]

        if primary_key == "":
            primary_key = columns[0]["name"]
            logger.info(
                f"No primary key specified, defaulting to first column: {primary_key}"
            )

        if order_by_column == "":
            if len(columns) > 1 and columns[1]["name"] != primary_key:
                order_by_column = columns[1]["name"]
            else:
                order_by_column = primary_key
            logger.info(
                f"No ORDER BY column specified, defaulting to column: {order_by_column}"
            )

        create_table_statement += f"  PRIMARY KEY ({primary_key})\n"
        if primary_key != order_by_column:
            create_table_statement += (
                f") ENGINE = MergeTree ORDER BY ({primary_key}, {order_by_column});\n\n"
            )
        else:
            create_table_statement += (
                f") ENGINE = MergeTree ORDER BY ({primary_key});\n\n"
            )

        return create_table_statement

    def generate_insert_row(
        self,
        table_name: str,
        rows: List[
            List[Union[str, int, bool, float, datetime.date, datetime.datetime]]
        ],
        columns: List[Dict[str, Union[str, bool]]],
        batch_size: int = 100000,
    ) -> str:
        logger.info(
            "Inserting rows",
            table_name=table_name,
            rows_count=len(rows),
            columns=columns,
        )
        column_names = ", ".join([column["name"] for column in columns])

        insert_into_statements = []

        for batch_start in range(0, len(rows), batch_size):
            batch_rows = rows[batch_start: batch_start + batch_size]
            insert_into_statement = (
                f"INSERT INTO {self.schema_name}.{table_name} ({column_names}) VALUES "
            )

            for i, row in enumerate(batch_rows):
                row_values = ""
                for j, column in enumerate(columns):
                    if j >= len(row):
                        raise ValueError(
                            f"Invalid row: {row}. It does not contain enough elements to access index {j}."
                        )
                    value = ""
                    if column["generator"] == "increment":
                        start = int(column["params"].get("start", 1))
                        step = int(column["params"].get("step", 1))
                        value = str(start + i * step)
                    else:
                        if self.data_types[column["dataType"]] == "Int32":
                            value = str(int(row[j]))
                        elif self.data_types[column["dataType"]] in [
                            "Decimal32(2)",
                            "Decimal64(2)",
                        ]:
                            value = str(row[j])
                        elif self.data_types[column["dataType"]] in "Float":
                            value = str(row[j])
                        elif self.data_types[column["dataType"]] == "Bool":
                            value = "1" if row[j] == "true" else "0"
                        elif self.data_types[column["dataType"]] == "String":
                            value = f"'{str(row[j])}'"
                        elif self.data_types[column["dataType"]] == "Date":
                            value = f"'{row[j]}'"
                        elif self.data_types[column["dataType"]] == "DateTime":
                            datetime_object = datetime.datetime.strptime(
                                row[j], "%Y-%m-%dT%H:%M:%S"
                            )
                            value = f"'{datetime_object.strftime('%Y-%m-%dT%H:%M:%S')}'"
                        else:
                            raise ValueError(
                                "Unknown data type: " + column["dataType"])

                    row_values += value
                    if j < len(columns) - 1:
                        row_values += ", "
                insert_into_statement += f"({row_values}), "

            insert_into_statement = insert_into_statement.rstrip(", ") + ";"
            insert_into_statements.append(insert_into_statement)
        return "\n".join(insert_into_statements)
