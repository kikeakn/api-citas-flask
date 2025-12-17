import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# Carga .env si existe (para Mongo Atlas en Apache/mod_wsgi)
def _load_dotenv(path: str = os.path.join(APP_DIR, ".env")) -> None:
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

_load_dotenv()

from application import app as application  # noqa: E402
