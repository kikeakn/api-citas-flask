# tests/conftest.py
import pytest
import mongomock

import application  # importamos el módulo entero


DB_NAME = "Clinica"


def _setup_test_db():
    """
    Prepara una base de datos en memoria para los tests usando mongomock.
    No necesita mongod ni tocar nada del servidor.
    """
    # 1) Crear un cliente de Mongo simulado
    mock_client = mongomock.MongoClient()

    # 2) Sustituir el cliente real de la app por el simulado
    application.myclient = mock_client

    # 3) Trabajar con la BD "Clinica" dentro de este cliente falso
    db = mock_client[DB_NAME]

    # Limpiar colecciones relevantes
    db["usuarios"].delete_many({})
    db["citas"].delete_many({})
    db["centros"].delete_many({})

    # Semilla mínima de centros para que los tests tengan datos coherentes
    db["centros"].insert_many(
        [
            {
                "name": "Centro de Salud Madrid Norte",
                "address": "Calle de la Salud, 123, Madrid",
            },
            {
                "name": "Centro Médico Madrid Sur",
                "address": "Avenida de la Medicina, 456, Madrid",
            },
        ]
    )

    return mock_client


@pytest.fixture
def client():
    """
    Fixture de pytest que devuelve un test_client de Flask
    con una BD limpia en cada test.
    """
    application.app.config["TESTING"] = True
    _setup_test_db()

    with application.app.test_client() as client:
        yield client
