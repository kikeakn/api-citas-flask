"""Script de migración inicial para la base de datos Clinica.

Crea las colecciones necesarias y añade índices y datos de ejemplo
para que la API pueda funcionar desde el primer arranque.
"""
import os
from typing import Iterable

import pymongo


MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("MONGODB_DB", "Clinica")


def ensure_collections(db: pymongo.database.Database, names: Iterable[str]) -> None:
    """Crea las colecciones listadas si no existen todavía."""
    existing = set(db.list_collection_names())
    for name in names:
        if name not in existing:
            db.create_collection(name)


def ensure_indexes(db: pymongo.database.Database) -> None:
    """Configura índices básicos para las colecciones principales."""
    db["usuarios"].create_index("username", unique=True)
    db["citas"].create_index(
        [("day", pymongo.ASCENDING), ("hour", pymongo.ASCENDING), ("center", pymongo.ASCENDING)],
        unique=True,
        name="unique_date_per_center",
    )


def seed_centers(db: pymongo.database.Database) -> None:
    """Inserta centros por defecto si la colección está vacía."""
    if db["centros"].count_documents({}) > 0:
        return

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


def main() -> None:
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]

    ensure_collections(db, ["usuarios", "centros", "citas"])
    ensure_indexes(db)
    seed_centers(db)

    print(
        "Migración completada. Base de datos '{db}' en '{uri}' lista para usarse.".format(
            db=DB_NAME, uri=MONGO_URI
        )
    )


if __name__ == "__main__":
    main()
