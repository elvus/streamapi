# StreamAPI

A Flask-based video streaming API with FFmpeg processing capabilities.

## Features

- Video upload and conversion to HLS format
- Background processing queue for FFmpeg conversions
- Process status tracking and awaiting
- Support for TV shows and movies
- JWT authentication

## FFmpeg Queue System

The API includes a robust queue system for handling FFmpeg video conversions:

### Starting the Queue Processor

Before uploading videos, start the background queue processor:

```bash
curl -X POST http://localhost:5000/v1/api/videos/queue/start
```

### Uploading Videos

Upload a video file:

```bash
curl -X POST http://localhost:5000/v1/api/videos/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@video.mp4" \
  -F "type=movie" \
  -F "values={\"title\":\"My Movie\",\"release_year\":2024}"
```

The upload will return a UUID that you can use to track the conversion process.

### Checking Process Status

Check the status of a conversion process:

```bash
curl http://localhost:5000/v1/api/videos/process/UUID_HERE/status
```

Possible status values:
- `queued`: Process is waiting in the queue
- `running`: Process is currently converting
- `completed`: Process finished successfully
- `failed`: Process failed
- `not_found`: UUID not found

### Awaiting Process Completion

Wait for a process to complete (with timeout):

```bash
curl -X POST http://localhost:5000/v1/api/videos/process/UUID_HERE/await \
  -H "Content-Type: application/json" \
  -d '{"timeout": 300}'
```

### Queue Information

Get information about the current queue:

```bash
curl http://localhost:5000/v1/api/videos/queue/info
```

### Cleanup

Clean up completed processes:

```bash
curl -X POST http://localhost:5000/v1/api/videos/queue/cleanup
```

## Usage Examples

### Python Example

```python
import requests
import time

# Start the queue processor
requests.post('http://localhost:5000/v1/api/videos/queue/start')

# Upload a video
with open('video.mp4', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/v1/api/videos/upload',
        headers={'Authorization': 'Bearer YOUR_TOKEN'},
        files={'file': f},
        data={
            'type': 'movie',
            'values': '{"title": "My Movie", "release_year": 2024}'
        }
    )

# Get the UUID from the response
uuid = response.json()['id']

# Check status periodically
while True:
    status_response = requests.get(f'http://localhost:5000/v1/api/videos/process/{uuid}/status')
    status = status_response.json()['process_status']
    
    if status == 'completed':
        print("Video conversion completed!")
        break
    elif status == 'failed':
        print("Video conversion failed!")
        break
    
    time.sleep(5)  # Wait 5 seconds before checking again

# Or await completion directly
await_response = requests.post(
    f'http://localhost:5000/v1/api/videos/process/{uuid}/await',
    json={'timeout': 300}
)
```

### JavaScript Example

```javascript
// Start the queue processor
await fetch('http://localhost:5000/v1/api/videos/queue/start', {
    method: 'POST'
});

// Upload a video
const formData = new FormData();
formData.append('file', videoFile);
formData.append('type', 'movie');
formData.append('values', JSON.stringify({
    title: 'My Movie',
    release_year: 2024
}));

const uploadResponse = await fetch('http://localhost:5000/v1/api/videos/upload', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN'
    },
    body: formData
});

const { id: uuid } = await uploadResponse.json();

// Check status
const checkStatus = async () => {
    const response = await fetch(`http://localhost:5000/v1/api/videos/process/${uuid}/status`);
    const { process_status } = await response.json();
    return process_status;
};

// Poll for completion
while (true) {
    const status = await checkStatus();
    
    if (status === 'completed') {
        console.log('Video conversion completed!');
        break;
    } else if (status === 'failed') {
        console.log('Video conversion failed!');
        break;
    }
    
    await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
}
```

## Configuration

The following configuration options are available for the FFmpeg queue:

- `HLS_SEGMENT_TIME`: Duration of each HLS segment (default: 10 seconds)
- `HLS_LIST_SIZE`: Number of segments to keep in playlist (default: 0 = all)
- `HLS_SEGMENT_TYPE`: Type of segments (default: 'fmp4')
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 2GB)

## Error Handling

The queue system includes comprehensive error handling:

- Process timeouts (configurable)
- Automatic cleanup of completed processes
- Status tracking for all processes
- Graceful handling of failed conversions

## Notes

- The queue processor runs as a background thread
- Processes are tracked by UUID for easy identification
- Failed processes are automatically marked as failed
- Original video files are cleaned up after successful conversion
- The system supports multiple concurrent conversions
