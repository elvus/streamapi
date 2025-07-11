from datetime import datetime
from bson import ObjectId
from flask import Blueprint, current_app, jsonify, request
from models.objectid import PydanticObjectId
from models.user_model import User
from flask_jwt_extended import jwt_required

from models.viewers_model import Viewer
from utils.hash import hash_password

users = Blueprint('users', __name__)

@users.route('/v1/api/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        db = current_app.config['db']
        cursor = db.users.find()
        users = [User(**doc).to_json() for doc in cursor]
        return jsonify(users), 200
    except Exception as e:
        print(e)
        return {'status': 'failed'}, 500
    
@users.route('/v1/api/users/<path:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        db = current_app.config['db']
        object_id = ObjectId(user_id)
        cursor = db.users.find_one({'_id': object_id})
        user = User(**cursor).to_json()
        return {'status': 'success', 'user': user}, 200
    except Exception as e:
        print(e)
        return {'status': 'failed'}, 500

@users.route('/v1/api/users', methods=['POST'])
@jwt_required()
def create_user():
    try:
        db = current_app.config['db']
        raw_data = request.get_json()
        password = hash_password(raw_data.pop('password'))
        user = User(**raw_data, password=password)
        insert_result = db.users.insert_one(user.to_bson())
        viewer = Viewer(name=user.username, status='active', use_pin=False, user_uuid=user.uuid)
        db.viewers.insert_one(viewer.to_bson())
        return {'status': 'success', 'id': str(insert_result.inserted_id)}, 201
    except Exception as e:
        print(e)
        return {'status': 'failed'}, 500
    
@users.route('/v1/api/users/<path:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        db = current_app.config['db']
        raw_data = request.get_json()
        user = User(**raw_data)
        user.updated_at = datetime.now()
        update_result = db.users.update_one({'_id': user_id}, {'$set': user.to_bson()})
        return {'status': 'success', 'id': str(update_result.upserted_id)}, 200
    except Exception as e:
        print(e)
        return {'status': 'failed'}, 500

@users.route('/v1/api/users/<path:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        db = current_app.config['db']
        delete_result = db.users.delete_one({'_id': PydanticObjectId(user_id)})
        return {'status': 'success', 'id': str(delete_result.deleted_count)}, 200
    except Exception as e:
        print(e)
        return {'status': 'failed'}, 500