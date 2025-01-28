from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_jwt_extended import create_refresh_token

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
        
        if not username or not password:
            return {'status': 'failed', 'msg': 'Username and password are required'}, 400
        
        cursor = db.users.find_one({'username': username})
        if cursor is None or not User.verify_password(User(**cursor), password):
            return {'status': 'failed', 'msg': 'Username or password is incorrect'}, 401
        
        user = User(**cursor)
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        response = jsonify({'status': 'success', 'user': user.to_json()})
        response.set_cookie('access_token_cookie', access_token, httponly=True, samesite='Lax')  # SameSite can be Strict if no cross-origin
        response.set_cookie('refresh_token_cookie', refresh_token, httponly=True, samesite='Lax')
        return response, 200
    
    except Exception as e:
        print(e)
        return {"status": "failed", "msg": "Internal server error"}, 500

@authentication.route('/v1/stream/app/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return {'status': 'success', 'access_token': access_token}, 200


@authentication.route('/v1/stream/app/register', methods=['POST'])
def register():
    try:
        raw_data = request.get_json()
        username = raw_data.get('username')
        password = raw_data.get('password')
        email = raw_data.get('email')
        privileges = ['read', 'write', 'update']
        user = User(username=username, password=password, email=email, privileges=privileges)
        cursor = db.users.find_one({'username': username})
        
        if cursor is not None:
            return {'status': 'failed', 'msg': 'Username already exists'}, 400
        
        db.users.insert_one(user.to_bson())
        return {'status': 'success', 'msg': 'User created successfully'}, 200
    except Exception as e:
        return {"status": "failed", "msg": "Internal server error"}, 500