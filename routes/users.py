from flask import Blueprint, current_app
from connection.connection import Connection
users = Blueprint('users', __name__)

@users.route('/v1/stream/app/users', methods=['GET'])
def get_users():
    try:
        conn = Connection()
        users = conn.get_users()
        return {'status': 'success', 'users': users}
    except Exception as e:
        print(e)
        return {'status': 'failed'}