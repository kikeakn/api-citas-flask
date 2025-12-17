import os
import pymongo


def _load_dotenv(path: str = ".env") -> None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k, v)
    except FileNotFoundError:
        pass


def main() -> None:
    _load_dotenv()

    mongo_uri = (
        os.environ.get("MONGODB_URI")
        or os.environ.get("MONGODB_URI_EACON")
        or "mongodb://localhost:27017/"
    )

    client = pymongo.MongoClient(mongo_uri)

    db = client["Clinica"]
    usuarios = db["usuarios"]
    centros = db["centros"]
    citas = db["citas"]

    # índices (idempotentes)
    try:
        usuarios.create_index("username")
    except Exception:
        pass

    try:
        citas.create_index([("day", 1), ("hour", 1), ("center", 1), ("cancel", 1)])
    except Exception:
        pass

    # Centros por defecto si no hay ninguno
    if centros.count_documents({}) == 0:
        centros.insert_many([
            {"name": "Centro de Salud Madrid Norte", "address": "Calle de la Salud, 123, Madrid"},
            {"name": "Centro Médico Madrid Sur", "address": "Avenida de la Medicina, 456, Madrid"},
        ])

    print("[INIT] OK: BD Clinica lista (Atlas/local).")


if __name__ == "__main__":
    main()
