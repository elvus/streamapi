import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from routes.stream import stream
from routes.users import users

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'flv', 'mkv', 'mov', 'wmv', 'webm'}
app.register_blueprint(stream)
app.register_blueprint(users)

CORS(app)


if __name__ == '__main__':
    app.run()