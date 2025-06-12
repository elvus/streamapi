from collections import defaultdict
from uuid import uuid4
from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from pathlib import Path
from ffmpeg import _ffmpeg as ffmpeg
from ffmpeg import probe as ffprobe
from connection.connection import Connection
from flask_cors import cross_origin
from multiprocessing import Process
import os
import json
from typing import List, Dict, Any
import logging

from models.catalog_model import StreamContent
from connection.connection import Connection

stream = Blueprint('stream', __name__)
conn = Connection()
db = conn.get_db()

logger = logging.getLogger(__name__)

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
    upload_path = os.path.join(base_path, *subdirs)
    os.makedirs(upload_path, exist_ok=True)
    return upload_path

def _generate_thumbnail(video_path, output_path):
    print("start thumbnail")
    try:
        (
            ffmpeg.input(video_path, ss='00:00:05')
            .output(output_path, vframes=1)
            .run(capture_stdout=True, capture_stderr=True)
        )
        print("finish thumbnail")
        return True
    except Exception:
        return False

def _validate_video_type(vtype):
    """Validate and normalize video type"""
    vtype = vtype.lower()
    if vtype in ['tv-shows', 'tvshow']:
        return 'tvshow'
    elif vtype == 'movies':
        return 'movie'
    return None

def _get_upload_structure(video_type, metadata=None):
    if video_type == 'tvshow':
        name = secure_filename(metadata['name'])
        season = f"S{str(metadata['season']).zfill(2)}"  # Pad season with leading zeros
        episode = f"E{str(metadata['episode']).zfill(2)}"  # Pad episode with leading zeros
        return [name, season, episode]
    elif video_type == 'movie':
        return []
    else:
        return {'status': 'failed', 'message': 'Invalid video type'}, 400

def _create_upload_path(base_path, video_type, subdirs, filename):
    if video_type == 'tvshow':
        # For TV shows, filename is not included in the directory structure
        return _create_upload_directory(base_path, *subdirs)
    else:
        # For movies, include filename in the directory structure
        return _create_upload_directory(base_path, *subdirs, filename)

def _get_video_duration(video_path: str) -> float:
    """
    Get the duration of a video file using ffprobe.
    Args:
        video_path (str): Path to the video file.
    Returns:
        float: Duration of the video in seconds.
    """
    try:
        duration = ffprobe(video_path)["format"]["duration"]
        return duration
    except Exception as e:
        current_app.logger.error(f'Error getting video duration: {str(e)}')
        return 0.0

def _add_to_ffmpeg_queue(uuid, file, video_type, metadata=None):
    """
    Add a video file to the FFmpeg conversion queue
    Returns: (video_path, video_output_path, process)
    """
    try:
        # Validate file
        if file.filename == '':
            return None, None, {'status': 'failed', 'message': 'No selected file'}, 400
        if not _allowed_file(file.filename):
            return None, None, {'status': 'failed', 'message': 'File type not allowed'}, 400
        if file.content_length > current_app.config.get('MAX_FILE_SIZE', 2 * 1024 * 1024 * 1024):
            return None, None, {'status': 'failed', 'message': 'File size exceeds maximum allowed'}, 400

        # Get upload structure based on video type and metadata
        subdirs_or_error = _get_upload_structure(video_type, metadata) if metadata else []
        if isinstance(subdirs_or_error, tuple):
            return None, None, subdirs_or_error

        # Create upload directory
        full_filename = secure_filename(file.filename)
        filename = Path(full_filename).stem
        upload_path = _create_upload_path(
            current_app.config['UPLOAD_FOLDER'],
            video_type,
            subdirs_or_error,
            filename
        )
        # Define paths
        video_path = os.path.join(upload_path, full_filename)
        video_output_path = os.path.join(upload_path, filename + '.m3u8')

        # Skip if output already exists
        if os.path.exists(video_output_path):
            return None, video_output_path, None

        # Save original file
        file.save(video_path)

        # Generate thumbnail
        thumbnail_path = os.path.join(upload_path, 'thumbnail.jpg')
        _generate_thumbnail(video_path, thumbnail_path)

        # Get HLS config
        hls_config = {
            'hls_segment_time': current_app.config.get('HLS_SEGMENT_TIME', 10),
            'hls_list_size': current_app.config.get('HLS_LIST_SIZE', 0),
            'hls_segment_type': current_app.config.get('HLS_SEGMENT_TYPE', 'fmp4')
        }

        # Start conversion process
        p = Process(target=_convert_video_to_hls, args=(
            uuid,
            video_path,
            video_output_path,
            hls_config['hls_segment_time'],
            hls_config['hls_list_size'],
            hls_config['hls_segment_type']
        ))
        p.start()

        return video_path, video_output_path, p

    except Exception as e:
        current_app.logger.error(f'Queue error: {str(e)}')
        if 'video_path' in locals() and os.path.exists(video_path):
            os.remove(video_path)
        return None, None, None

def _convert_video_to_hls(uuid, video_path, video_output_path, hls_segment_time=10, hls_list_size=0, hls_segment_type='fmp4'):
    """Convert video to HLS format with improved error handling and logging"""
    try:
        # Create temporary directory for segments
        hls_params = {
            'format': 'hls',
            'acodec': 'copy',
            'vcodec': 'libx264',
            'start_number': 0,
            'hls_time': hls_segment_time,
            'hls_list_size': hls_list_size,
            'hls_segment_type': hls_segment_type,
            'hls_flags': 'independent_segments',
        }
        # Run conversion
        (
            ffmpeg.input(video_path)
            .output(video_output_path, **hls_params)
            .run(capture_stdout=True, capture_stderr=True)
        )
        _update_status(uuid)
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        # Print finish message
        print("finish conversion")
        # Clean up the original video file after conversion
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"Deleted original video file: {video_path}")

def _get_season_episodes(seasons: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    """
    Organize episodes by season from a list of season data.

    Args:
        seasons (List[Dict[str, Any]]): List of season data containing episode information.

    Returns:
        Dict[int, List[Dict[str, Any]]]: A dictionary where keys are season numbers and values are lists of episode data.
    """
    episodes = defaultdict(list)
    
    for season in seasons:
        try:
            season_number = season['season']
            episode_data = {
                'title': season['title'],
                'episode_number': season['episode']
            }
            
            if 'intro_start_time' in season and season['intro_start_time']:
                episode_data['intro_start_time'] = season['intro_start_time']
                episode_data['intro_end_time'] = season['intro_end_time']
            
            if 'next_episode_time' in season and season['next_episode_time']:
                episode_data['next_episode_time'] = season['next_episode_time']

            episodes[season_number].append(episode_data)
        except KeyError as e:
            logger.error(f"Missing key in season data: {e}")
            continue
    
    return episodes

def _update_status(content_id: str) -> bool:
    """
    Update the status of a content item to "Ready" in the database.
    
    Args:
        content_id (str): The UUID of the content to update
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        result = db.catalog.update_one(
            {'uuid': content_id},
            {'$set': {'status': 'Ready'}}
        )
        
        if result.modified_count > 0:
            logger.info(f'Successfully updated status to Ready for content {content_id}')
            return True
        else:
            logger.warning(f'No content found with ID {content_id} to update status')
            return False
            
    except Exception as e:
        logger.error(f'Error updating status for content {content_id}: {str(e)}')
        return False

@stream.route('/v1/api/videos/stream/<path:filename>', methods=['GET'])
def stream_video(filename):
    #ffmpeg -i input.mkv -c:v libx264 -c:a aac -f dash -hls_segment_type fmp4 output.m`pd
    return send_file(filename, mimetype='application/x-mpegURL')
    
@stream.route('/v1/api/videos', methods=['GET'])
def list_content():
    try:
        cursor = db.catalog.find()
        content = [StreamContent(**item).to_json() for item in cursor]
        return jsonify(content), 200
    except Exception as e:
        return {'status': 'failed', 'message': str(e)}, 500

@stream.route('/v1/api/videos/<string:vtype>/list', methods=['GET'])
def list_content_by_type(vtype):
    try:
        # Validate and normalize video type
        normalized_type = _validate_video_type(vtype)
        if not normalized_type:
            return {'status': 'failed', 'message': 'Invalid content type. Use "tv-shows" or "movies"'}, 400        
        # Query database with pagination support
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        skip = (page - 1) * per_page
        
        # Get total count for pagination
        total_count = db.catalog.count_documents({'type': normalized_type})
        
        # Query with pagination
        cursor = db.catalog.find(
            {'type': normalized_type},
            skip=skip,
            limit=per_page
        )
        
        # Convert results to JSON
        content = [StreamContent(**item).to_json() for item in cursor]
        
        return jsonify({
            'status': 'success',
            'data': content,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': (total_count + per_page - 1) // per_page
            }
        }), 200
        
    except ValueError as e:
        return {'status': 'failed', 'message': 'Invalid pagination parameters'}, 400
    except Exception as e:
        current_app.logger.error(f'Error listing content: {str(e)}')
        return {'status': 'failed', 'message': 'Internal server error'}, 500

@stream.route('/v1/api/videos/<string:content_id>/season/<int:season>', methods=['GET'])
def get_episode(content_id, season):
    try:
        # Validate content_id and season
        if not content_id or not isinstance(season, int):
            return {'status': 'failed', 'message': 'Invalid content_id or season'}, 400
        
        # Aggregate query to find the specific episode
        cursor = db.catalog.aggregate([
            { 
                "$match": {
                    "uuid": content_id,
                    "seasons.season_number": season
                }
            },
            {
                "$unwind": "$seasons"
            },
            {
                "$unwind": "$seasons.episodes"
            },
            {
                "$project": {
                    "uuid": 1,
                    "title": 1,
                    "release_year": 1,
                    "genre": 1,
                    "rating": 1,
                    "type": { "$literal": "video" },
                    "season_number": "$seasons.season_number",
                    "episode": "$seasons.episodes.episode_number",
                    "intro_start_time": "$seasons.episodes.intro_start_time",
                    "intro_end_time":"$seasons.episodes.intro_end_time",
                    "next_episode_time": "$seasons.episodes.next_episode_time",
                    "file_path": "$seasons.episodes.file_path",
                    "_id": 0
                }
            }
        ])
        
        # Collect all results into a list
        results = list(cursor)
        
        # Check if the list is empty
        if not results:
            return {'status': 'failed', 'message': 'Content not found'}, 404
        
        # Close the cursor to free up resources
        cursor.close()
        
        return jsonify(results), 200
        
    except Exception as e:
        current_app.logger.error(f'Error fetching episode: {str(e)}')
        return {'status': 'failed', 'message': 'Internal server error'}, 500

@stream.route('/v1/api/videos/<string:content_id>/details', methods=['GET'])
def get_content(content_id):
    try:
        cursor = db.catalog.find_one({'uuid': content_id})
        if cursor is None:
            return {'status': 'failed', 'message': 'Content not found'}, 404
        return jsonify(StreamContent(**cursor).to_json()), 200
    except Exception as e:
        return {'status': 'failed', 'message': str(e)}, 500

@stream.route('/v1/api/videos/upload', methods=['POST'])
@jwt_required()
def upload_video():
    """Handle video upload with improved error handling and async processing"""
    try:
        # Validate request
        validation_error = _validate_upload_request(request)
        if validation_error:
            return validation_error
        
        uuid = str(uuid4())
        video_type = request.form['type']
        values = json.loads(request.form['values'])
        values['status'] = "In-Progress"
        values['uuid'] = uuid
        if video_type == 'tvshow':
            # Handle multiple files for TV shows
            metadata_list = request.form.getlist('metadata')
            files = request.files.getlist('file')
            values['type'] = video_type
            values['seasons'] = []
            episodes = _get_season_episodes(values['show_details'])
            # Process each file with its metadata
            for file, metadata in zip(files, metadata_list):
                metadata = json.loads(metadata)
                video_path, video_output_path, process = _add_to_ffmpeg_queue(uuid, file, video_type, metadata)
                if isinstance(process, tuple):  # Error case
                    return process
                                
                if process or video_output_path:  # New conversion started or file already exists
                    for episode in episodes[metadata['season']]:
                        if episode['episode_number'] == metadata['episode']:
                            episode['file_path'] = video_output_path
                            episode['duration_seconds'] = _get_video_duration(video_path)
                    if len(values['seasons']) > 0:
                        if metadata['season'] not in [s['season_number'] for s in values['seasons']]:
                            values['seasons'].append({
                                'season_number': metadata['season'],
                                'episodes': episodes[metadata['season']]
                            })
                    else:
                        values['seasons'].append({
                            'season_number': metadata['season'],
                            'episodes': episodes[metadata['season']]
                        })
        else:
            # Handle single file for movies
            file = request.files['file']
            video_path, video_output_path, process = _add_to_ffmpeg_queue(uuid, file, video_type)
            if isinstance(process, tuple):  # Error case
                return process
            
            if process or video_output_path:  # New conversion started
                values['file_path'] = video_output_path
                values['duration_seconds'] = _get_video_duration(video_path)
        content = StreamContent(**values)
        insert_result = db.catalog.insert_one(content.to_bson())
        return {'status': 'success', 'id': str(insert_result.inserted_id)}, 201
        
    except Exception as e:
        current_app.logger.error(f'Upload error: {str(e)}')
        return {'status': 'failed', 'message': str(e)}, 500
    
@stream.route('/v1/api/videos', methods=['POST'])
@jwt_required()
def create_content():
    try:
        raw_data = request.get_json()
        content = StreamContent(**raw_data)
        insert_result = db.catalog.insert_one(content.to_bson())
        return {'status': 'success', 'id': str(insert_result.inserted_id)}, 201
    except Exception as e:
        return {'status': 'failed', 'message': str(e)}, 500