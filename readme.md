# API de Citas con Flask y MongoDB

API sencilla para gestionar usuarios, centros y citas médicas usando Flask, JWT y MongoDB.

## Requisitos previos
- Python 3.10 o superior
- MongoDB en ejecución y accesible
- (Opcional) Entorno virtual para aislar dependencias

## Configuración del entorno
1. Clona el repositorio y entra en la carpeta del proyecto.
2. Crea y activa un entorno virtual (recomendado):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Variables de entorno
Configura la conexión a MongoDB y Flask (usa los valores por defecto si no las defines):
```bash
export MONGODB_URI="mongodb://localhost:27017/"
export MONGODB_DB="Clinica"
export FLASK_APP=application.py
export FLASK_ENV=development
```

## Ejecución de migraciones
Ejecuta el script de migración para crear las colecciones, índices y centros de ejemplo:
```bash
python migrations/001_init_clinica.py
```
El script usa `MONGODB_URI` y `MONGODB_DB` para conectarse.

## Iniciar la API
Arranca el servidor de desarrollo en la red local:
```bash
flask run --host=0.0.0.0 --port=5000
```
La documentación Swagger estará disponible en `http://localhost:5000/apidocs`.

## Flujos básicos
- **Registro**: `POST /register` con `username`, `password` y datos del usuario.
- **Login**: `POST /login` devuelve un token JWT.
- **Centros**: `GET /centers` requiere token en el encabezado `Authorization: Bearer <token>`.
- **Citas**: Endpoints `/date/create`, `/date/getByDay`, `/date/getByUser`, `/date/delete` y `/dates` para gestionar citas.

## Notas
- Ejecuta el script de migración cada vez que montes un entorno nuevo.
- Asegúrate de que MongoDB esté en marcha antes de iniciar la API.
- Utiliza herramientas como Postman o `curl` para probar los endpoints.
