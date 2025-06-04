import os
from flask import Flask
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from routes.stream import stream
from routes.users import users
from routes.authentication import authentication
from routes.healthz import healthz

# Load environment variables
load_dotenv()

# Flask app configuration
app = Flask(__name__)
jwt = JWTManager(app)

# CORS configuration
CORS(app, supports_credentials=True, origins=os.getenv('CORS_ORIGIN', 'http://localhost:5173').split(','))

# File upload configuration
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/code/uploads')
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'flv', 'mkv', 'mov', 'wmv', 'webm'}

# JWT configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  # Store JWT in cookies
app.config["JWT_COOKIE_SECURE"] = True  # Set to True in production (HTTPS only)
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Set to True for CSRF protection
app.config["JWT_COOKIE_SAMESITE"] = 'None'  # Allow cookies to be sent with cross-site requests

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
