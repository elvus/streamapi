import os
from flask import Flask
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from routes.stream import stream
from routes.users import users
from routes.authentication import authentication
from routes.healthz import healthz

load_dotenv()

app = Flask(__name__)
jwt = JWTManager(app)
CORS(app, supports_credentials=True, origins=os.getenv('CORS_ORIGIN').split(','))

app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'flv', 'mkv', 'mov', 'wmv', 'webm'}
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  # Store JWT in cookies
app.config["JWT_COOKIE_SECURE"] = False  # Set to True in production (HTTPS only)
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Set to True for CSRF protection


app.register_blueprint(stream)
app.register_blueprint(users)
app.register_blueprint(authentication)
app.register_blueprint(healthz)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT') or 5000)
