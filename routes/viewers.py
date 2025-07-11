from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from models.viewers_model import Viewer
from utils.hash import hash_password

viewers = Blueprint('viewers', __name__)

@viewers.route('/v1/api/viewers', methods=['GET'])
@jwt_required()
def get_viewers():
    try:
        db = current_app.config['db']
        cursor = db.viewers.find({'user_uuid': get_jwt()['user_uuid']})
        viewers = [Viewer(**doc).to_json() for doc in cursor]
        return jsonify(viewers), 200
    except Exception as e:
        print(e)
        return {'status': 'failed'}, 500

@viewers.route('/v1/api/viewers/<path:viewer_uuid>', methods=['GET'])
@jwt_required()
def get_viewer(viewer_uuid):
    try:
        db = current_app.config['db']
        cursor = db.viewers.find_one({'uuid': viewer_uuid})
        viewer = Viewer(**cursor).to_json()
        return jsonify(viewer), 200
    except Exception as e:
        print(e)
        return {'status': 'failed'}, 500

@viewers.route('/v1/api/viewers', methods=['POST'])
@jwt_required()
def create_viewer():
    try:
        db = current_app.config['db']
        raw_data = request.get_json()
        viewer = Viewer(**raw_data, user_uuid=get_jwt()['user_uuid'])
        insert_result = db.viewers.insert_one(viewer.to_bson())
        return jsonify({'status': 'success', 'id': str(insert_result.inserted_id)}), 201
    except Exception as e:
        print(e)
        return {'status': 'failed'}, 500

@viewers.route('/v1/api/viewers/<path:viewer_uuid>', methods=['PUT'])
@jwt_required()
def update_viewer(viewer_uuid):
    try:
        db = current_app.config['db']
        raw_data = request.get_json()
        pin = hash_password(raw_data.pop('pin'))
        viewer = Viewer(**raw_data, pin=pin)
        db.viewers.update_one({'uuid': viewer_uuid}, {'$set': viewer})
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(e)
        return {'status': 'failed'}, 500
        
@viewers.route('/v1/api/viewers/<path:viewer_uuid>', methods=['DELETE'])
@jwt_required()
def delete_viewer(viewer_uuid):
    try:
        db = current_app.config['db']
        db.viewers.delete_one({'uuid': viewer_uuid})
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(e)
        return {'status': 'failed'}, 500