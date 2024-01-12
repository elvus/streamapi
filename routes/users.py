from datetime import datetime
from bson import ObjectId
from flask import Blueprint, current_app, request
from models.user_model import User
from connection.connection import Connection
users = Blueprint('users', __name__)
conn = Connection()
db = conn.get_db()

@users.route('/v1/stream/app/users', methods=['GET'])
def get_users():
    try:
        cursor = db.users.find()
        return {'status': 'success', 'users': [User(**doc).to_json() for doc in cursor]}
    except Exception as e:
        print(e)
        return {'status': 'failed'}
    
@users.route('/v1/stream/app/users/<path:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        object_id = ObjectId(user_id)
        cursor = db.users.find_one({'_id': object_id})
        user = User(**cursor).to_json()
        return {'status': 'success', 'user': user}
    except Exception as e:
        print(e)
        return {'status': 'failed'}

@users.route('/v1/stream/app/users', methods=['POST'])
def create_user():
    try:
        raw_data = request.get_json()
        user = User(**raw_data)
        user.created_at = datetime.now()
        insert_result = db.users.insert_one(user.to_bson())
        return {'status': 'success', 'id': str(insert_result.inserted_id)}
    except Exception as e:
        print(e)
        return {'status': 'failed'}
    
@users.route('/v1/stream/app/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        raw_data = request.get_json()
        user = User(**raw_data)
        user.updated_at = datetime.now()
        update_result = db.users.update_one({'_id': user_id}, {'$set': user.to_bson()})
        return {'status': 'success', 'id': str(update_result.upserted_id)}
    except Exception as e:
        print(e)
        return {'status': 'failed'}

@users.route('/v1/stream/app/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        delete_result = db.users.delete_one({'_id': user_id})
        return {'status': 'success', 'id': str(delete_result.deleted_count)}
    except Exception as e:
        print(e)
        return {'status': 'failed'}
    
@users.route('/v1/stream/app/login', methods=['POST'])
def login(username, password):
    try:
        user = db.users.find_one({'username': username, 'password': password})
        return {'status': 'success', 'user': str(user)}
    except Exception as e:
        return {'status': 'failed'}
