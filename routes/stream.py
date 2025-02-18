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
    except Exception as e:
        return {'status': 'failed', 'message': str(e)}, 500

@stream.route('/v1/api/videos/<string:content_id>/details', methods=['GET'])
def get_content(content_id):
    try:
        conn = Connection()
        db = conn.get_db()
        cursor = db.catalog.find_one({'uuid': content_id})
        if cursor is None:
            return {'status': 'failed', 'message': 'Content not found'}, 404
        return jsonify(StreamContent(**cursor).to_json()), 200
    except Exception as e:
        return {'status': 'failed', 'message': str(e)}, 500
    
@stream.route('/v1/api/videos/upload', methods=['POST'])
@jwt_required()
def upload_video():
    try:
        # Validate file exists in request
        if 'file' not in request.files:
            return {'status': 'failed', 'message': 'No file part in the request'}, 400
            
        file = request.files['file']
        
        # Validate file is selected and allowed
        if file.filename == '':
            return {'status': 'failed', 'message': 'No selected file'}, 400
            
        if not allowed_file(file.filename):
            return {'status': 'failed', 'message': 'File type not allowed'}, 400

        # Create secure paths
        full_filename = secure_filename(file.filename)
        filename = Path(full_filename).stem
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Create directory if it doesn't exist
        os.makedirs(upload_path, exist_ok=True)

        # Save original file
        video_path = os.path.join(upload_path, full_filename)
        file.save(video_path)
        
        # Convert to HLS
        video_output_path = os.path.join(upload_path, filename + '.m3u8')
        try:
            (
                ffmpeg.input(video_path)
                .output(video_output_path, 
                       format='hls',
                       acodec='copy',
                       vcodec='libx264',
                       start_number=0,
                       hls_time=10,
                       hls_list_size=0,
                       hls_segment_type='fmp4')
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            # Clean up if conversion fails
            os.remove(video_path)
            return {'status': 'failed', 'message': f'Video conversion failed: {e.stderr.decode()}'}, 500

        # Clean up original file
        os.remove(video_path)
        
        return jsonify({
            'status': 'success',
            'file_path': video_output_path,
            'message': 'Video uploaded and converted successfully'
        }), 200
        
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