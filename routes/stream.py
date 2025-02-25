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

def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def _validate_upload_request(request):
    if 'file' not in request.files:
        return {'status': 'failed', 'message': 'No file part in the request'}, 400
    if 'type' not in request.form:
        return {'status': 'failed', 'message': 'Type parameter is required'}, 400
    return None

def _create_upload_directory(base_path, *subdirs):
    print(subdirs)
    upload_path = os.path.join(base_path, *subdirs)
    os.makedirs(upload_path, exist_ok=True)
    return upload_path

def _generate_thumbnail(video_path, output_path):
    try:
        (
            ffmpeg.input(video_path, ss='00:00:01')
            .output(output_path, vframes=1)
            .run(capture_stdout=True, capture_stderr=True)
        )
        return True
    except ffmpeg.Error:
        return False

def _validate_tvshow_fields(request):
    required_fields = ['name', 'season', 'episode']
    missing_fields = [field for field in required_fields if field not in request.form]
    if missing_fields:
        return {'status': 'failed', 'message': f'Missing required fields: {", ".join(missing_fields)}'}, 400
    return None

def _get_upload_structure(video_type, request):
    if video_type == 'tvShow':
        validation_error = _validate_tvshow_fields(request)
        if validation_error:
            return validation_error
            
        name = secure_filename(request.form['name'])
        season = f"season{request.form['season'].zfill(2)}"  # Pad season with leading zeros
        episode = f"episode{request.form['episode'].zfill(2)}"  # Pad episode with leading zeros
        return [name, season, episode]
    elif video_type == 'movie':
        return []
    else:
        return {'status': 'failed', 'message': 'Invalid video type'}, 400

def _create_upload_path(base_path, video_type, subdirs, filename):
    if video_type == 'tvShow':
        # For TV shows, filename is not included in the directory structure
        return _create_upload_directory(base_path, *subdirs)
    else:
        # For movies, include filename in the directory structure
        return _create_upload_directory(base_path, *subdirs, filename)

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
        # Validate request
        validation_error = _validate_upload_request(request)
        if validation_error:
            return validation_error
            
        file = request.files['file']
        video_type = request.form['type']
        
        # Validate file
        if file.filename == '':
            return {'status': 'failed', 'message': 'No selected file'}, 400
        if not _allowed_file(file.filename):
            return {'status': 'failed', 'message': 'File type not allowed'}, 400
        if file.content_length > current_app.config.get('MAX_FILE_SIZE', 2 * 1024 * 1024 * 1024):  # Default 2GB
            return {'status': 'failed', 'message': 'File size exceeds maximum allowed'}, 400

        # Validate video type specific fields
        subdirs_or_error = _get_upload_structure(video_type, request)
        if isinstance(subdirs_or_error, tuple):  # If it's an error response
            return subdirs_or_error
        subdirs = subdirs_or_error

        # Create upload directory
        full_filename = secure_filename(file.filename)
        filename = Path(full_filename).stem
        upload_path = _create_upload_path(
            current_app.config['UPLOAD_FOLDER'],
            video_type,
            subdirs,
            filename
        )

        # Save original file
        video_path = os.path.join(upload_path, full_filename)
        file.save(video_path)
        
        # Generate thumbnail
        thumbnail_path = os.path.join(upload_path, 'thumbnail.jpg')
        thumbnail_generated = _generate_thumbnail(video_path, thumbnail_path)
        
        # Convert to HLS
        video_output_path = os.path.join(upload_path, filename + '.m3u8')
        try:
            hls_params = {
                'format': 'hls',
                'acodec': 'copy',
                'vcodec': 'libx264',
                'start_number': 0,
                'hls_time': current_app.config.get('HLS_SEGMENT_TIME', 10),
                'hls_list_size': current_app.config.get('HLS_LIST_SIZE', 0),
                'hls_segment_type': current_app.config.get('HLS_SEGMENT_TYPE', 'fmp4'),
                'hls_flags': 'independent_segments'
            }
            
            (
                ffmpeg.input(video_path)
                .output(video_output_path, **hls_params)
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            # Clean up if conversion fails
            os.remove(video_path)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            current_app.logger.error(f'Video conversion failed: {e.stderr.decode()}')
            return {'status': 'failed', 'message': 'Video conversion failed'}, 500

        # Clean up original file
        os.remove(video_path)
        
        return jsonify({
            'status': 'success',
            'file_path': video_output_path,
            'thumbnail_path': thumbnail_path if thumbnail_generated else None,
            'message': 'Video uploaded and converted successfully',
            'type': video_type,
            'metadata': {
                'season': subdirs[1] if video_type == 'tvShow' else None,
                'episode': subdirs[2] if video_type == 'tvShow' else None
            }
        }), 200
        
    except Exception as e:
        print(e)
        return {'status': 'failed', 'message': 'Internal server error'}, 500
    
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