from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from pathlib import Path
from ffmpeg import _ffmpeg as ffmpeg
from ffmpeg import _probe as ffprobe
from connection.connection import Connection
from flask_cors import cross_origin
import os

from models.catalog_model import StreamContent
from connection.connection import Connection

stream = Blueprint('stream', __name__)
conn = Connection()
db = conn.get_db()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@stream.route('/v1/api/videos/stream/<path:filename>', methods=['GET'])
def stream_video(filename):
    #ffmpeg -i input.mkv -c:v libx264 -c:a aac -f dash -hls_segment_type fmp4 output.m`pd
    return send_file(filename, mimetype='application/x-mpegURL')
    
@stream.route('/v1/api/videos', methods=['GET'])
def list_content():
    try:
        conn = Connection()
        db = conn.get_db()
        cursor = db.catalog.find()
        content = [StreamContent(**item).to_json() for item in cursor]
        return jsonify(content), 200

        # content = []
        # for root, dirs, files in os.walk(current_app.config['UPLOAD_FOLDER']):
        #     for file in files:
        #         if file.endswith('.m3u8'):
        #             content.append({
        #                 'key': Path(file).stem,
        #                 'id': Path(file).stem,
        #                 'title': Path(file).stem,
        #                 'duration_seconds': ffprobe.probe(os.path.join(root, file))['format']['duration'],
        #                 'path': os.path.join(root, file)
        #             })
        # return jsonify(content), 200
    except Exception as e:
        return {'status': 'failed', 'message': str(e)}, 500

@stream.route('/v1/api/videos/<string:content_id>/details', methods=['GET'])
def get_content(content_id):
    try:
        print(content_id)
        conn = Connection()
        db = conn.get_db()
        cursor = db.catalog.find_one({'uuid': content_id})
        return jsonify(StreamContent(**cursor).to_json()), 200
    except Exception as e:
        return {'status': 'failed', 'message': str(e)}, 500
    
@stream.route('/v1/api/videos/upload', methods=['POST'])
@jwt_required()
def upload_video():
    #convert video to hls = ffmpeg -i demo.flv -codec:a copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls demo.m3u8
    try:
        file = request.files['file']
        if file and allowed_file(file.filename):
            full_filename = secure_filename(file.filename)
            filename = Path(full_filename).stem
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            if not os.path.exists(upload_path):
                os.makedirs(upload_path)

            video_path = os.path.join(upload_path, full_filename)
            file.save(video_path)
            
            video_output_path = os.path.join(upload_path, filename + '.m3u8')
            ffmpeg.input(video_path).output(video_output_path, format='hls', acodec='copy', start_number=0, hls_time=10, hls_list_size=0).run()

            os.remove(video_path)
        return jsonify({'status': 'success', 'file_path': video_output_path}), 200
    except Exception as e:
        return {'status': 'failed', 'message': str(e)}, 500
    
@stream.route('/v1/api/videos', methods=['POST'])
@jwt_required()
def create_content():
    try:
        conn = Connection()
        db = conn.get_db()
        raw_data = request.get_json()
        content = StreamContent(**raw_data)
        insert_result = db.catalog.insert_one(content.to_bson())
        return {'status': 'success', 'id': str(insert_result.inserted_id)}, 201
    except Exception as e:
        return {'status': 'failed', 'message': str(e)}, 500