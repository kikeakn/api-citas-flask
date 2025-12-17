import os
import uuid
import pytest
import pymongo

import application  # importa el módulo entero


@pytest.fixture(scope="session")
def mongo_uri():
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        pytest.fail("Falta MONGODB_URI en variables de entorno (ponlo en GitHub Secrets y en server).")
    return uri


@pytest.fixture(scope="session")
def test_db_name():
    # BD única por ejecución (evita pisar datos)
    base = os.environ.get("MONGODB_DB", "Clinica")
    suffix = os.environ.get("CI_DB_SUFFIX") or str(uuid.uuid4())[:8]
    return f"{base}_test_{suffix}"


@pytest.fixture(scope="session")
def mongo_client(mongo_uri):
    return pymongo.MongoClient(mongo_uri)


@pytest.fixture(scope="session", autouse=True)
def configure_app_db(monkeypatch, mongo_client, test_db_name):
    # Forzamos la BD de tests
    monkeypatch.setenv("MONGODB_URI", os.environ["MONGODB_URI"])
    monkeypatch.setenv("MONGODB_DB", test_db_name)

    # Resetea cliente cacheado si ya se importó
    application._mongo_client = mongo_client

    # Inicializa colecciones/índices/centros
    import importlib.util
    import pathlib

    path = pathlib.Path(__file__).resolve().parent.parent / "001_init_clinica.py"
    spec = importlib.util.spec_from_file_location("init_clinica", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    mod.main()  # crea colecciones/índices/centros en la BD de tests

    yield

    # Cleanup: borra la BD de test completa
    mongo_client.drop_database(test_db_name)


@pytest.fixture()
def client():
    application.app.config["TESTING"] = True
    with application.app.test_client() as c:
        yield c
