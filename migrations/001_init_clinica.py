"""
Script de migración inicial para la base de datos Clinica.

- Crea las colecciones necesarias (usuarios, centros, citas)
- Crea índices útiles
- Inserta centros de ejemplo (incluye 'Centro de Salud Madrid Norte')
- Inserta un usuario por defecto (kike / kike1234)
"""

import os
import bcrypt
from pymongo import MongoClient
from pymongo.database import Database


MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("MONGODB_DB", "Clinica")


def ensure_collections(db: Database) -> None:
    """Crea colecciones si no existen."""
    needed = {"usuarios", "centros", "citas"}
    existing = set(db.list_collection_names())

    for name in needed - existing:
        db.create_collection(name)
        print(f"[*] Colección creada: {name}")


def init_indexes(db: Database) -> None:
    """Crea índices para mejorar consultas y evitar duplicados."""

    citas = db["citas"]
    # Evitar citas duplicadas mismo día + hora + centro
    citas.create_index(
        [("day", 1), ("hour", 1), ("center", 1)],
        name="uniq_day_hour_center",
        unique=True,
    )
    print("[*] Índices de 'citas' OK")


def seed_centers(db: Database) -> None:
    """Inserta centros de ejemplo si aún no hay ninguno."""
    centers = db["centros"]
    if centers.count_documents({}) > 0:
        print("[*] Centros ya existen, no se insertan duplicados.")
        return

    docs = [
        {
            "name": "Centro de Salud Joyfe",
            "address": "Calle Vitalaza, 50, Madrid",
        },
        {
            "name": "Centro Médico Arturo Soria",
            "address": "Calle Arturo Soria, 456, Madrid",
        },
        {
            "name": "Centro de Salud Madrid Norte",
            "address": "Calle Alcalá 123, Madrid",
        }
    ]
    centers.insert_many(docs)
    print("[*] Insertados centros de ejemplo (Joyfe / Arturo Soria / Madrid Norte).")



def seed_default_user(db: Database) -> None:
    """Inserta un usuario por defecto para pruebas manuales."""
    users = db["usuarios"]
    username = "kike"

    if users.find_one({"username": username}):
        print("[*] Usuario existente.")
        return

    raw_password = "kike1234"
    hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    doc = {
        "username": username,
        "password": hashed,
        "name": "Kike",
        "lastname": "Acon",
        "email": "kike@joyfe.com",
        "phone": "600000000",
        "date": "01/01/2000",
    }

    users.insert_one(doc)
    print("[*] Usuario creado: kike / kike1234")


def main() -> None:
    print(f"Conectando a Mongo en {MONGO_URI!r}, BD '{DB_NAME}'...")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    ensure_collections(db)
    init_indexes(db)
    seed_centers(db)
    seed_default_user(db)

    print("[OK] Migración inicial completada.")


if __name__ == "__main__":
    main()
