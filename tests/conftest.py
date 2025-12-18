# tests/conftest.py
import os

import pytest
from pymongo import MongoClient

import application

# Datos de conexión (los mismos que usas en el workflow)
MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
BASE_DB_NAME = os.environ.get("MONGODB_DB", "Clinica")
CI_DB_SUFFIX = os.environ.get("CI_DB_SUFFIX", "local_test")

# Nombre de la base de datos SOLO para tests
TEST_DB_NAME = f"{BASE_DB_NAME}_test_{CI_DB_SUFFIX}"


def _reset_test_db(client: MongoClient):
    """
    Deja la base de datos de tests en un estado limpio e inicializado.
    """
    db = client[TEST_DB_NAME]

    # Limpieza por si vienen datos de ejecuciones anteriores
    for name in ["usuarios", "centros", "citas"]:
        db.drop_collection(name)

    # --- Centros de ejemplo (incluye el del test) ---
    centers = db["centros"]
    centers.insert_many(
        [
            {
                "name": "Centro de Salud Madrid Norte",
                "address": "Calle Falsa 123, Madrid",
            },
            {
                "name": "Centro de Salud Joyfe",
                "address": "Calle Vitalaza, 50, Madrid",
            },
            {
                "name": "Centro Médico Arturo Soria",
                "address": "Calle Arturo Soria, 456, Madrid",
            },
        ]
    )

    # --- Índices de citas ---
    citas = db["citas"]
    citas.create_index(
        [("day", 1), ("hour", 1), ("center", 1)],
        name="uniq_day_hour_center",
        unique=True,
    )

    return db


@pytest.fixture(scope="session")
def mongo_client():
    """
    Cliente Mongo real (Atlas) pero apuntando a la BD de tests.
    """
    client = MongoClient(MONGO_URI)
    _reset_test_db(client)
    return client


@pytest.fixture(scope="session")
def app(mongo_client):
    """
    Configura la aplicación Flask para que use la BD de tests.
    """
    # Forzamos a la app a usar la BD de pruebas
    application.DB_NAME = TEST_DB_NAME
    application.myclient = mongo_client

    application.app.config["TESTING"] = True
    return application.app


@pytest.fixture()
def client(app):
    """
    Test client de Flask. Se crea uno nuevo por cada test.
    """
    with app.test_client() as c:
        yield c
