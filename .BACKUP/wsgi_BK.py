import os
import sys

# Aseguramos que Flask pueda encontrar application.py
APP_DIR = "/var/www/alumnos/eacon/flask_app"
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/")
os.environ.setdefault("MONGODB_DB", "Clinica")

# Importamos la app de Flask desde application.py
from application import app as application  # <-- WSGI necesita 'application'
