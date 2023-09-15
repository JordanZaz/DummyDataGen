# test_app.py
import os
import pytest
import json
from flask import session
from app import app as flask_app
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated_client(app):
    client = app.test_client()

    response = client.post(
        "/api/auth",
        json={
            "username": os.getenv("USERNAME"),
            "password": os.getenv("PASSWORD"),
        },
    )

    assert response.status_code == 200
    assert response.get_json() == {"status": "success"}

    return client


def test_authenticate(client):
    # Test that correct credentials authenticate successfully
    response = client.post(
        "/api/auth",
        json={
            "username": os.getenv("USERNAME"),
            "password": os.getenv("PASSWORD"),
        },
    )
    assert response.status_code == 200
    assert response.get_json() == {"status": "success"}

    # Test that incorrect credentials fail to authenticate
    response = client.post(
        "/api/auth",
        json={
            "username": "incorrect",
            "password": "incorrect",
        },
    )
    assert response.status_code == 401
    assert response.get_json() == {"error": "Incorrect username or password"}


def test_is_authenticated(client):
    # Test that the session is not authenticated by default
    response = client.get("/api/is_authenticated")
    assert response.status_code == 401
    assert response.get_json() == {"status": "fail"}

    # Authenticate the session
    client.post(
        "/api/auth",
        json={
            "username": os.getenv("USERNAME"),
            "password": os.getenv("PASSWORD"),
        },
    )

    # Test that the session is now authenticated
    response = client.get("/api/is_authenticated")
    assert response.status_code == 200
    assert response.get_json() == {"status": "success"}


def test_generate_requires_auth(client):
    # Test that the generate route requires authentication
    response = client.post(
        "/generate", json={"dataSource": "dummy_source", "reportType": "dummy_report"}
    )
    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required"}


def test_generate(authenticated_client):
    data = {"dataSource": "valid_dataSource", "reportType": "valid_reportType"}
    response = authenticated_client.post(
        "/generate", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200


def test_generate_edited(authenticated_client):
    default_yaml = """
    rows: 5
    tableName: test
    """
    yaml = """
    columns:
      - name: field1
        dataType: string
        generator: email
    """
    data = {
        "defaultYaml": default_yaml,
        "yaml": yaml,
        "dataSource": "valid_dataSource",
        "reportType": "valid_reportType",
    }

    response = authenticated_client.post(
        "/generate_edited", data=json.dumps(data), content_type="application/json"
    )
    print(response.data)
    assert response.status_code == 200


def test_get_datasources(authenticated_client):
    response = authenticated_client.get("/get_datasources")
    assert response.status_code == 200


def test_get_report_types(authenticated_client):
    valid_datasource = "valid_datasource"
    response = authenticated_client.get(
        f"/get_report_types/{valid_datasource}")
    assert response.status_code == 200
