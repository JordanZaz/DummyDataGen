import pandas as pd
import sqlite3
import structlog

logger = structlog.get_logger(__name__)


def load_data_into_db():
    # Connect to SQLite database (or create it if it doesn't exist)
    with sqlite3.connect("test_sqlite.db") as conn:
        # Load the CSV data into Pandas DataFrames
        improvado_df = pd.read_csv("biz_data_dictionary.csv")
        queryme_df = pd.read_csv("mrt_report_types.csv")

        # Write the data from the dataframes into the SQLite database
        improvado_df.to_sql("biz_data_dictionary", conn,
                            if_exists="replace", index=False)
        queryme_df.to_sql("mrt_report_types", conn,
                          if_exists="replace", index=False)

        logger.info("Data imported successfully!")


if __name__ == "__main__":
    load_data_into_db()
