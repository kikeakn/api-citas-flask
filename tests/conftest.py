# tests/conftest.py
import pytest
from application import app, myclient  # myclient es el MongoClient global


DB_NAME = "Clinica"  # misma que la app; solo borramos datos de pruebas


def _reset_database():
    """Deja la BD en un estado conocido SOLO para los usuarios de test."""
    db = myclient[DB_NAME]

    # Borrar solo los usuarios de prueba que crean los tests
    db["usuarios"].delete_many(
        {"username": {"$in": ["usuario_test", "user_dates"]}}
    )

    # Borrar solo citas de esos usuarios
    db["citas"].delete_many(
        {"user": {"$in": ["usuario_test", "user_dates"]}}
    )

    # Centros: si están vacíos, los creamos; si ya hay, no tocamos nada
    if db["centros"].count_documents({}) == 0:
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


@pytest.fixture
def client():
    app.config["TESTING"] = True
    _reset_database()

    with app.test_client() as client:
        yield client
