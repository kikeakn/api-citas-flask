# tests/test_basic.py
import pytest

import application


@pytest.fixture
def client():
    app = application.app
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_root_endpoint(client):
    resp = client.get("/")
    assert resp.status_code == 200
    # Buscamos nuestro mensaje dentro del HTML
    assert b"tiene que fallar" in resp.data


def test_apidocs_accessible(client):
    resp = client.get("/apidocs/")
    assert resp.status_code == 200
