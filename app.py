import os
import sqlite3
from datetime import timedelta
from functools import wraps
from settings import AGENCY_ID, USERNAME, PASSWORD, SCHEMA_NAME

import yaml
import structlog
from dotenv import load_dotenv
from flask import Flask, request, jsonify, session, g, url_for
from flask.helpers import send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from typing import Dict, List, Union, Any

from backend.clickhouse_client import client, table_exists
from data.main import generate_data_from_yaml, generate_query_from_yaml
from backend.generate_json import generate_table_meta, get_connection, clean_string

logger = structlog.get_logger(__name__)

load_dotenv()
app = Flask(__name__, static_folder='generate_json/build', static_url_path=os.getenv("STATIC_URL_PATH", "/"))
app.config["SECRET_KEY"] = os.urandom(24)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=6)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
limiter = Limiter(get_remote_address, app=app)
CORS(app, supports_credentials=True)


def login_required(f):
    @wraps(f)
    def decorated_function(*args: List, **kwargs: Dict) -> Union[jsonify, Any]:
        if "authenticated" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)

    return decorated_function


@app.route("/generate", methods=["POST"])
@login_required
def generate() -> Union[jsonify, Any]:
    logger.info("Processing generate request")
    data = request.get_json()
    datasource = data.get("dataSource")
    report_type = data.get("reportType")

    yaml_data: Dict[str, Union[List, int]] = {"columns": []}
    rows = yaml_data.get("rows")

    table_name = yaml_data.get("tableName")

    if not datasource or not report_type:
        user_id = AGENCY_ID
        datasource = "dummy_source"
        report_type = "dummy_report"

        if not table_name:
            table_name = f"dummy_report_{user_id}_dummy_source"
    else:
        if not table_name:
            table_name = f"{clean_string(report_type).lower()}_{AGENCY_ID}_{clean_string(datasource).lower()}_all_data"

    if rows is not None and rows <= 0:
        error_message = {
            "error": "Invalid number of rows: must be a positive number"}
        logger.error("Invalid number of rows: must be a positive number")
        return jsonify(error_message), 400

    table_meta_params: Dict[str, Union[str, int]] = {
        "user_id": AGENCY_ID,
        "datasource": datasource,
        "report_type": report_type,
        "table_name": table_name,
    }

    try:
        result = generate_table_meta(**table_meta_params)
    except ValueError as e:
        error_message = {"error": str(e)}
        logger.error("Failed to generate table metadata", exc_info=True)
        return jsonify(error_message), 400

    if result is None:
        error_message = {
            "error": "An error occurred while generating table metadata. Please try again."
        }
        logger.error(
            "An unexpected error occurred while generating table metadata")
        return jsonify(error_message), 500

    logger.info("Successfully generated table metadata")
    return jsonify(result)


@app.route("/generate_edited", methods=["POST"])
@login_required
def generate_edited() -> Union[jsonify, Any]:
    logger.info("Processing generate_edited request")
    try:
        data = request.get_json()
        default_yaml_string = data.get("defaultYaml")
        yaml_string = data.get("yaml")
        datasource = data.get("dataSource")
        report_type = data.get("reportType")

        combined_yaml_string = f"{default_yaml_string}\n{yaml_string}"

        try:
            yaml_parsed = yaml.safe_load(combined_yaml_string)
        except yaml.YAMLError as e:
            error_message = {
                "error": f"Invalid YAML format. Make sure the spacing and indentation is the same."
            }
            return jsonify(error_message), 400

        if yaml_parsed is None:
            error_message = {
                "error": "Datasource and report type must be specified."}
            return jsonify(error_message), 400

        rows = yaml_parsed.get("rows", None)
        if rows is None or not isinstance(rows, int) or rows <= 0:
            error_message = {
                "error": "Invalid rows value. Must be a positive integer."}
            return jsonify(error_message), 400

        yaml_table_name = yaml_parsed.get("tableName")

        if datasource and report_type:
            table_name = f"{clean_string(report_type).lower()}_{AGENCY_ID}_{clean_string(datasource).lower()}_all_data"
        elif yaml_table_name:
            table_name = yaml_table_name
        else:
            agency_id = AGENCY_ID
            table_name = f"dummy_report_{agency_id}_dummy_source"

        yaml_parsed["tableName"] = table_name

        yaml_string_with_table_name = yaml.dump(
            yaml_parsed, default_flow_style=False)

        create_table_statement, insert_row_statements = generate_data_from_yaml(
            yaml_string_with_table_name
        )

        if table_exists(table_name, SCHEMA_NAME):
            client.command(
                f"DROP TABLE IF EXISTS {SCHEMA_NAME}.{table_name} SYNC")

        client.command(create_table_statement)
        for statement in insert_row_statements.split(";"):
            if statement.strip():
                client.command(statement)

        return jsonify(
            {
                "parsed_yaml": yaml_parsed,
                "query_from_yaml": generate_query_from_yaml(
                    yaml_string_with_table_name
                ),
                "yaml_string_with_table_name": yaml_string_with_table_name,
            }
        )
    except Exception as e:
        logger.error(
            "An unexpected error occurred in generate_edited", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/get_datasources", methods=["GET"])
@login_required
def get_datasources() -> Union[jsonify, Any]:
    logger.info("Processing get_datasources request")
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT DISTINCT datasource_title
            FROM biz_data_dictionary
        """
        )

        datasources = [row["datasource_title"] for row in cursor.fetchall()]
        return jsonify(datasources)
    except sqlite3.Error as e:
        logger.error("Error while getting datasources", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route("/get_report_types/<datasource>", methods=["GET"])
@login_required
def get_report_types(datasource: str) -> Union[jsonify, Any]:
    logger.info(f"Processing get_report_types request for {datasource}")
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT DISTINCT report_type_title
            FROM biz_data_dictionary
            WHERE datasource_title = ?
        """,
            (datasource,),
        )

        report_types = [row["report_type_title"] for row in cursor.fetchall()]
        return jsonify(report_types)
    except sqlite3.Error as e:
        logger.error("Error while getting report types", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/auth", methods=["POST"])
def authenticate() -> Union[jsonify, Any]:
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
        correct_username = USERNAME
        correct_password = PASSWORD

        if username == correct_username:
            if password == correct_password:
                session["authenticated"] = True
                return jsonify({"status": "success"}), 200

    session.pop("authenticated", None)
    return jsonify({"error": "Incorrect username or password"}), 401


@app.route("/api/is_authenticated", methods=["GET"])
def is_authenticated() -> Union[jsonify, Any]:
    if "authenticated" in session:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "fail"}), 401


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path: str) -> Any:
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0')

