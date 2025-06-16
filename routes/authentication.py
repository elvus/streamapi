from datetime import datetime
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended.exceptions import JWTDecodeError


from models.objectid import PydanticObjectId
from models.user_model import User

authentication = Blueprint('authentication', __name__)

@authentication.route('/v1/api/auth/login', methods=['POST'])
def login():
    try:
        db = current_app.config['db']
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
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response, 200
    
    except Exception as e:
        print(e)
        return {"status": "failed", "msg": "Internal server error"}, 500

@authentication.route('/v1/api/auth/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return {'status': 'success', 'access_token': access_token}, 200


@authentication.route('/v1/api/auth/register', methods=['POST'])
def register():
    try:
        db = current_app.config['db']
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
    
@authentication.route('/v1/api/auth/logout', methods=['DELETE'])
@jwt_required()
def logout():
    try:
        db = current_app.config['db']
        # Get the JWT token
        jwt = get_jwt()
        jti = jwt["jti"]
        
        # Add the token to the blacklist
        db.token_blacklist.insert_one({
            "jti": jti,
            "created_at": datetime.now(),
            "expires_at": datetime.fromtimestamp(jwt["exp"])
        })
        
        response = jsonify({"status": "success", "msg": "logout successful"})
        unset_jwt_cookies(response)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"status": "failed", "msg": "Failed to logout"}), 500

@authentication.route('/v1/api/auth/check', methods=['GET'])
@jwt_required()
def check_auth():
    try:
        db = current_app.config['db']
        user_id = get_jwt_identity()
        user = db.users.find_one({'_id': PydanticObjectId(user_id)})
        if user:
            return {'status': 'success', 'authenticated': True, 'user': User(**user).to_json()}, 200
        return {'status': 'failed', 'authenticated': False, 'msg': 'User not found'}, 401
    except Exception as e:
        return {'status': 'failed', 'authenticated': False, 'msg': 'Invalid token'}, 401
