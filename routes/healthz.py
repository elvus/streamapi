from flask import Blueprint, request
from datetime import datetime

healthz = Blueprint('healthz', __name__)

@healthz.route('/healthz', methods=['GET'])
def healthz_check():
    return {'status': 'success', 'message': "Service is up and running"}, 200

@healthz.route('/healthz/ping', methods=['GET'])
def ping():
    return {'message': "pong"}, 200

@healthz.route('/healthz/ready', methods=['GET'])
def ready():
    return {'status': 'success', 'message': f"Service is ready at {datetime.now()}"}, 200   
