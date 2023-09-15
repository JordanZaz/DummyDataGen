import sqlite3
import yaml
import re
import structlog
from .keywords import (
    int_keywords,
    string_keywords,
    date_keywords,
    email_keywords,
    float_keywords,
    keyword_ranges,
    dictionary_keywords,
)
from typing import List, Dict, Any, Union, Tuple

logger = structlog.get_logger(__name__)


def get_connection() -> sqlite3.Connection:
    try:
        conn = sqlite3.connect("test_sqlite.db")
        conn.row_factory = sqlite3.Row
        logger.info("Database connection established successfully.")
        return conn
    except sqlite3.Error as e:
        logger.error("Error connecting to the database.", exception=str(e))
        raise ValueError("Error connecting to the database.")


def clean_string(s):
    return re.sub(r"\W+", "_", s)


def infer_datatype_and_generator(column_name: str, used_increment: bool) -> Tuple[str, str, Dict[str, Any], bool]:
    for dictionary_type, keywords in dictionary_keywords.items():
        if any(keyword in column_name for keyword in keywords):
            return (
                "string",
                "dictionary",
                {"dictionary_type": dictionary_type},
                used_increment,
            )
    if "_id" in column_name and not used_increment:
        return "int", "increment", {"start": 1, "step": 1}, True
    elif any(keyword in column_name for keyword in int_keywords):
        min_val, max_val = next(
            (
                keyword_ranges[k]
                for k in keyword_ranges
                if (
                    "_" + k + "_" in column_name
                    or column_name.startswith(k + "_")
                    or column_name.endswith("_" + k)
                    or column_name == k
                )
            ),
            (1, 10000),
        )
        return "int", "range", {"min": min_val, "max": max_val}, used_increment
    elif any(keyword in column_name for keyword in email_keywords):
        return "string", "email", {}, used_increment
    elif any(keyword in column_name for keyword in date_keywords):
        return "date", "date", {"format": "YYYY-MM-DD"}, used_increment
    elif any(keyword in column_name for keyword in float_keywords):
        min_val, max_val = next(
            (
                keyword_ranges[k]
                for k in keyword_ranges
                if (
                    "_" + k + "_" in column_name
                    or column_name.startswith(k + "_")
                    or column_name.endswith("_" + k)
                    or column_name == k
                )
            ),
            (0.0, 10000.0),
        )
        return "float", "range", {"min": min_val, "max": max_val}, used_increment
    elif any(keyword in column_name for keyword in string_keywords):
        length = next(
            (
                keyword_ranges[k]
                for k in keyword_ranges
                if (
                    "_" + k + "_" in column_name
                    or column_name.startswith(k + "_")
                    or column_name.endswith("_" + k)
                    or column_name == k
                )
            ),
            20,
        )
        return "string", "random", {"length": length}, used_increment
    else:
        return "string", "random", {"length": 10}, used_increment


def generate_table_meta(
    user_id: int, datasource: str, report_type: str, table_name: str = None
) -> Dict[str, Any]:

    if table_name is None:
        table_name = f"{clean_string(report_type).lower()}_{user_id}_{clean_string(datasource).lower()}_all_data"

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT *
                FROM biz_data_dictionary
                WHERE datasource_title = ?
                    AND report_type_title = ?
            """,
                (datasource, report_type),
            )
        except sqlite3.Error as e:
            logger.error("Error executing SQL query.", exception=str(e))
            raise ValueError(f"Error executing SQL query: {e}")

        rows_data = cursor.fetchall()

        table_meta = {"columns": [], "tableName": table_name}

        used_increment = False
        for row in rows_data:
            datatype, generator, params, used_increment = infer_datatype_and_generator(
                row["field_sql_name"], used_increment
            )
            column_info = {
                "name": row["field_sql_name"],
                "dataType": datatype,
                "generator": generator,
            }
            if params:
                column_info["params"] = params
            table_meta["columns"].append(column_info)

        return table_meta

    finally:
        if conn:
            conn.close()
