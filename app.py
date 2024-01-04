from flask import Flask, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import ffmpeg
import os

load_dotenv()

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'flv', 'mkv', 'mov', 'wmv', 'webm'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
CORS(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/v1/stream/app/<path:filename>', methods=['GET'])
def stream_video(filename):
    #ffmpeg -i input.mkv -c:v libx264 -c:a aac -f dash -hls_segment_type fmp4 output.m`pd
    hls_path = 'videos/' + filename  # Replace with the actual path to your MPD files
    return send_file(hls_path, mimetype='application/x-mpegURL')

@app.route('/v1/stream/app/upload', methods=['POST'])
#convert video to hls = ffmpeg -i demo.flv -codec:a copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls demo.m3u8
def upload_video():
    try:
        file = request.files['file']
        if file and allowed_file(file.filename):
            full_filename = secure_filename(file.filename)
            filename = os.path.splitext(filename)[0]
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)            
            if not os.path.exists(path):
                os.mkdir(path)

            video_path = os.path.join(path, full_filename)
            video_name = os.path.join(path, filename)
            
            file.save(video_path)
            ffmpeg.input(video_path).output(video_name + '.m3u8', format='hls', acodec='copy', start_number=0, hls_time=10, hls_list_size=0).run()
            os.remove(video_path)
        return {'status': 'success'}
    except Exception as e:
        print(e)
        return {'status': 'failed'}
    
@app.route('/v1/stream/app/content', methods=['GET'])
def get_content():
    try:
        content = []
        for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
            for file in files:
                if file.endswith('.m3u8'):
                    content.append(os.path.join(root[len(app.config['UPLOAD_FOLDER']):], file))
        return {'status': 'success', 'catalog': { 'title': 'Random Videos', 'content': content }}
    except Exception as e:
        print(e)
        return {'status': 'failed'}
    
if __name__ == '__main__':
    app.run()