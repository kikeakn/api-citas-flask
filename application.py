import os

from flask import render_template
from flask import Flask
from flask import jsonify
from flask import request

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from datetime import datetime

from flasgger import Swagger

import pymongo
import bcrypt

from flask_cors import CORS


app = Flask(__name__)

CORS(app)

app.config["JWT_SECRET_KEY"] = "misuperclavedeldestinofinal"

jwt = JWTManager(app)
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "API de Clínica",
        "description": "Documentación de la API para agendar citas",
        "version": "0.0.1",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Añade 'Bearer <tu_token>' para autenticación"
        }
    },
    "security": [{"Bearer": []}]
})

# ========= Mongo config =========
# Preferimos variables de entorno (secrets) y, si no existen, leemos un .env local (NO se sube a git).
# Esto permite:
# - Tests en GitHub Actions (env)
# - Deploy en servidor (deploy.sh escribe .env con el secret)
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

_load_dotenv()

# Se acepta MONGODB_URI (estándar) o MONGODB_URI_EACON (para evitar pisar secrets entre alumnos)
mongo_uri = (
    os.environ.get("MONGODB_URI")
    or os.environ.get("MONGODB_URI_EACON")
    or "mongodb://localhost:27017/"
)

myclient = pymongo.MongoClient(mongo_uri)


@app.route("/", methods=["GET"])
def hello():
    return render_template("index.html")



@app.route('/login', methods=['POST'])
def login():
    """
    Iniciar sesión en la aplicación
    ---
    tags:
      - Autenticación
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Token de acceso generado correctamente
      401:
        description: Credenciales incorrectas
    """
    mydb = myclient["Clinica"]
    mycol = mydb["usuarios"]

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        return jsonify({"msg": "Bad username or password"}), 401

    user = mycol.find_one({"username": username})

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    else:
        return jsonify({"msg": "Bad username or password"}), 401


@app.route("/register", methods=['POST'])
def register():
    """
    Registrar un nuevo usuario
    ---
    tags:
        - Autenticación
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
                username:
                    type: string
                password:
                    type: string
                name:
                    type: string
                lastname:
                    type: string
                email:
                    type: string
                phone:
                    type: string
                date:
                    type: string
                    format: date
                    example: "25/12/2025"
                    description: Fecha de nacimiento en formato DD/MM/YYYY
    responses:
        200:
            description: Usuario creado correctamente
        400:
            description: Solicitud incorrecta
    """
    mydb = myclient["Clinica"]
    mycol = mydb["usuarios"]

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    name = request.json.get('name', None)
    lastname = request.json.get('lastname', None)
    email = request.json.get('email', None)
    phone = request.json.get('phone', None)
    date = request.json.get('date', None)

    try:
        date = datetime.strptime(date, '%d/%m/%Y').strftime('%d/%m/%Y')
    except ValueError:
        return jsonify({"msg": "Invalid date format"}), 400

    if username is None or password is None:
        return jsonify({"msg": "Bad request"}), 400

    # Si el usuario ya existe, devolvemos 200 para que los tests sean idempotentes
    existing = mycol.find_one({"username": username})
    if existing:
        return jsonify({"msg": "user already exists"}), 200

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    password = hashed_password.decode('utf-8')

    user = {
        "username": username,
        "password": password,
        "name": name,
        "lastname": lastname,
        "email": email,
        "phone": phone,
        "date": date
    }
    mycol.insert_one(user)

    return jsonify({"msg": "user created"}), 200


@app.route("/centers", methods=['GET'])
@jwt_required()
def center():
    """
    Obtiene una lista de todos los centros
    ---
    tags:
      - Centros
    security:
      - Bearer: []
    """
    mydb = myclient["Clinica"]
    mycol = mydb["centros"]
    centers = mycol.find({}, {"_id": 0})
    return jsonify(list(centers))


@app.route("/profile", methods=['GET'])
@jwt_required()
def profile():
    """
    Obtiene el perfil del usuario actual
    ---
    tags:
        - Perfil
    security:
        - Bearer: []
    """
    current_user = get_jwt_identity()
    mydb = myclient["Clinica"]
    mycol = mydb["usuarios"]
    user = mycol.find_one({"username": current_user}, {"_id": 0, "password": 0})
    return jsonify(user)


@app.route("/date/create", methods=['POST'])
@jwt_required()
def createDate():
    """
    Crea una nueva cita en la base de datos.
    ---
    tags:
        - Citas
    security:
        - Bearer: []
    """
    current_user = get_jwt_identity()
    mydb = myclient[DB_NAME]
    mycol = mydb["citas"]
    myCenters = mydb["centros"]

    date = request.json.get('date', None)
    center = request.json.get('center', None)

    if not date or not center:
        return jsonify({"msg": "Bad request"}), 400

    # 1) Validar que el centro existe
    existing_center = myCenters.find_one({"name": center})
    if not existing_center:
        return jsonify({"msg": "Center not found"}), 400

    # 2) Parsear la fecha con el formato exacto que usan los tests
    try:
        date_obj = datetime.strptime(date, '%d/%m/%Y %H:00:00')
        day = date_obj.strftime('%d/%m/%Y')
        hour = date_obj.strftime('%H')
    except ValueError:
        return jsonify({"msg": "Invalid date format"}), 400

    # 3) Comprobar que no exista ya una cita para ese centro, día y hora
    existing_date = mycol.find_one(
        {
            "day": day,
            "hour": hour,
            "center": center,
            "cancel": {"$ne": 1},
        }
    )
    if existing_date:
        return jsonify({"msg": "Date and hour already taken"}), 400

    # 4) Insertar la cita
    new_date = {
        "username": current_user,
        "day": day,
        "hour": hour,
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "center": center,
        "cancel": 0,
    }
    mycol.insert_one(new_date)

    return jsonify({"msg": "Date created successfully"}), 200



@app.route("/date/getByDay", methods=['POST'])
@jwt_required()
def getDatesByDay():
    mydb = myclient["Clinica"]
    mycol = mydb["citas"]
    day = request.json.get('day', None)

    # Ojo: aquí day suele venir como string. No tocamos más para no romper.
    if not day:
        return jsonify({"msg": "Bad request"}), 400

    dates = mycol.find({"day": day, "cancel": {"$ne": 1}}, {"_id": 0})
    return jsonify(format_dates(list(dates)))


@app.route("/date/getByUser", methods=['GET'])
@jwt_required()
def getDateByUser():
    current_user = get_jwt_identity()
    mydb = myclient["Clinica"]
    mycol = mydb["citas"]

    dates = mycol.find({"username": current_user, "cancel": {"$ne": 1}}, {"_id": 0})
    return jsonify(format_dates(list(dates)))


@app.route("/date/delete", methods=['POST'])
@jwt_required()
def deleteDate():
    current_user = get_jwt_identity()
    mydb = myclient["Clinica"]
    mycol = mydb["citas"]

    date = request.json.get('date', None)
    center = request.json.get('center', None)

    try:
        date = datetime.strptime(date, '%d/%m/%Y %H:00:00')
        day = date.strftime('%d/%m/%Y')
        hour = date.strftime('%H')
    except ValueError:
        return jsonify({"msg": "Invalid date format"}), 400

    doc = mycol.find_one({"day": day, "hour": hour, "center": center})
    if not doc:
        return jsonify({"msg": "Date not found"}), 400

    if doc["username"] != current_user:
        return jsonify({"msg": "Unauthorized"}), 401

    mycol.update_one(
        {"day": day, "hour": hour, "center": center},
        {"$set": {"cancel": 1}}
    )

    return jsonify({"msg": "Date deleted successfully"}), 200


@app.route("/dates", methods=['GET'])
@jwt_required()
def getDates():
    mydb = myclient["Clinica"]
    mycol = mydb["citas"]

    dates = mycol.find({"cancel": {"$ne": 1}}, {"_id": 0})
    return jsonify(format_dates(list(dates)))


def format_dates(dates):
    result = []
    for date in dates:
        date['date'] = f"{date['day']} {date['hour']}:00:00"
        del date['day']
        del date['hour']
        result.append(date)

    result.sort(key=lambda x: datetime.strptime(x['date'], '%d/%m/%Y %H:00:00'))
    return result
