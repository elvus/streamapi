import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from routes.stream import stream
from routes.users import users
from routes.authentication import authentication

load_dotenv()

app = Flask(__name__)
jwt = JWTManager(app)
CORS(app)

app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'flv', 'mkv', 'mov', 'wmv', 'webm'}
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

app.register_blueprint(stream)
app.register_blueprint(users)
app.register_blueprint(authentication)

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT') or 5000)
