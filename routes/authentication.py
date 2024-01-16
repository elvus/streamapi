from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from connection.connection import Connection
from models.user_model import User

authentication = Blueprint('authentication', __name__)
conn = Connection()
db = conn.get_db()

@authentication.route('/v1/stream/app/login', methods=['POST'])
def login():
    try:
        raw_data = request.get_json()
        username = raw_data.get('username')
        password = raw_data.get('password')
        cursor = db.users.find_one({'username': username, 'password': password})
        
        if cursor is None:
            return {'status': 'failed', 'msg': 'Username or password is incorrect'}, 401
        
        user = User(**cursor)
        access_token = create_access_token(identity=user.id)
        return {'status': 'success', 'user': user.to_json(), 'access_token': access_token}, 200
    except Exception as e:
        print(e)
        return {"status": "failed", "msg": "Internal server error"}, 500
