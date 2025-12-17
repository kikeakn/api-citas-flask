import os
import uuid
import pytest
import pymongo
import application


@pytest.fixture(scope="session")
def mongo_client():
    mongo_uri = os.environ.get("MONGODB_URI") or os.environ.get("MONGODB_URI_EACON")
    if not mongo_uri:
        raise RuntimeError("Falta MONGODB_URI (o MONGODB_URI_EACON) en variables de entorno")
    return pymongo.MongoClient(mongo_uri)


@pytest.fixture(scope="session")
def test_db_name():
    # DB única por ejecución para no pisar datos
    suffix = os.environ.get("CI_DB_SUFFIX") or str(uuid.uuid4()).replace("-", "")
    return f"Clinica_test_{suffix}"


@pytest.fixture(scope="function")
def configure_app_db(monkeypatch, test_db_name):
    # Cambiamos a nivel de app: usar DB de tests sin tocar producción
    monkeypatch.setenv("MONGODB_DB", test_db_name)
    yield


@pytest.fixture(scope="function")
def client(configure_app_db):
    application.app.config["TESTING"] = True
    with application.app.test_client() as c:
        yield c
