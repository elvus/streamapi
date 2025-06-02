# StreamAPI: FFMPEG API for Video Conversion

StreamAPI is a simple yet powerful FFMPEG-based API that allows you to effortlessly convert your videos into the widely used M3U8 format. With easy setup and execution, this tool streamlines the process of adapting your videos for various streaming applications.

## Requirements

To run StreamAPI, you need the following software installed on your system:

- Docker
- Python 3.6+
- FFMPEG
- MongoDB

## Installation

### Using Docker (Recommended)

```sh
# Clone the repository
git clone https://github.com/elvus/streamapi.git
cd streamapi

# Start the services
docker-compose up -d
```
### Manual Setup

```sh
# Clone the repository
git clone https://github.com/elvus/streamapi.git
cd streamapi
```

### 1. Create a Virtual Environment

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Rename `.env.example` to `.env`

Rename the provided `.env.example` file to `.env`. This file contains configuration settings for your StreamAPI.

### 5. Configure the `.env` File

1. Set the `UPLOAD_FOLDER` variable to the path where you want to save your converted videos.
2. Set your `JWT_SECRET_KEY` sentence
3. Set your `MONGO_URI` connection variables
4. Set the `CORS_ORIGIN` variable to the URL of your frontend application.

```env
UPLOAD_FOLDER=/path/to/your/upload/folder
JWT_SECRET_KEY=my_secret_key
MONGO_URI=mongodb://localhost:27017/streamapi
CORS_ORIGIN=http://localhost:3000
```

Replace `/path/to/your/upload/folder` with the actual directory path where you want to store the converted videos.

### 6. Run the Flask Application

```bash
export FLASK_APP=app.py
flask run
```

That's it! Your StreamAPI server is now up and running. You can now utilize the API to convert your videos to the M3U8 format seamlessly.

## Usage

To convert a video, send a POST request to the appropriate endpoint with the video file. The API will handle the conversion process and provide you with the M3U8 file for streaming.

```bash
curl -X POST -F "file=@your_video.mp4" http://localhost:3001/v1/api/videos/upload
```
Make sure to replace `your_video.mp4` with the actual file path of the video you want to convert.

## API Endpoints
### Authentication Endpoints
### 1. Register User
***Endpoint:*** `POST /v1/api/stream/register`
- **Description:** Registers a new user.
- **Request:**
  - Headers: `Content-Type: application/json`
  - Body:
    ```json
    {
      "username": "user",
      "password": "password",
      "email": "user@mail.com"
    }
    ```
- **Response:**
  ```json
  {
    "status": "success",
    "msg": "User created successfully"
  }
  ```
### 2. Login User 
***Endpoint:*** `POST /v1/api/stream/login`
- **Description:** Logs in a user.
- **Request:**
  - Headers: `Content-Type: application/json`
  - Body:
    ```json
    {
      "status": "success",
      "user": {
        "created_at": "Thu, 13 Feb 2025 00:10:01 GMT",
        "email": "user@mail.com",
        "id": "67ad38720cfcd6ffd43f131c",
        "password": "*********",
        "privileges": [
          "read",
          "write",
          "update"
        ],
        "profile": null,
        "role": null,
        "updated_at": null,
        "username": "user"
      }
    }

    ```
- **Response:**
  ```json
  {
    "status": "success",
    "msg": "Logged in successfully",
  }
  ```

### Video Endpoints
### 1. Upload Video

**Endpoint:** `POST /v1/api/videos/upload`

- **Description:** Uploads a video file.
- **Request:**
  - Headers: `Content-Type: multipart/form-data`
  - Body:
    - `file`: Video file
- **Response:**
  ```json
  {
    "status": "success",
    "file_path": "/path/to/your/upload/folder/video.m3u8"
  }
  ```

### 2. Stream Video

**Endpoint:** `GET /v1/api/videos/stream/:id`

- **Description:** Streams a video by ID.
- **Request:**
  - Params:
    - `id`: Video ID
- **Response:** Video stream

### 3. Get Video Metadata

**Endpoint:** `GET /v1/api/videos/:id/details`

- **Description:** Retrieves metadata for a stored video.
- **Request:**
  - Params:
    - `id`: Video ID
- **Response:**
  ```json
  {
    "cast": null,
    "created_at": "Wed, 12 Feb 2025 00:39:42 GMT",
    "description": null,
    "duration_seconds": null,
    "file_path": "/path/to/your/upload/folder/video.m3u8",
    "genre": [
      "Animation"
    ],
    "id": "67abedce3f77fbead839c165",
    "rating": 0,
    "release_year": 2025,
    "seasons": null,
    "title": "My Video",
    "type": "movie",
    "updated_at": "Wed, 12 Feb 2025 00:39:42 GMT",
    "uuid": "c8528052-b99e-425b-ad8a-53e9221ddd5e"
  }
  ```
### 4. Get All Videos
- **Endpoint:** `GET /v1/api/videos`
- **Description:** Retrieves all stored videos.
- **Request:** None
- **Response:**
    ```json
    [
        {
            "cast": null,
            "created_at": "Wed, 12 Feb 2025 00:39:42 GMT",
            "description": null,
            "duration_seconds": null,
            "file_path": "/path/to/your/upload/folder/video.m3u8",
            "genre": [
                "Animation"
            ],
            "id": "67abedce3f77fbead839c165",
            "rating": 0,
            "release_year": 2025,
            "seasons": null,
            "title": "My Video",
            "type": "movie",
            "updated_at": "Wed, 12 Feb 2025 00:39:42 GMT",
            "uuid": "c8528052-b99e-425b-ad8a-53e9221ddd5e"
        }
    ]
    ```
## UI Setup

StreamAPI comes with a user interface provided by the `streamui` repository. To set up the UI, follow these steps:

### 1. Clone the `streamui` Repository

```sh
git clone https://github.com/elvus/streamui.git
cd streamui
```

### 2. Install Dependencies

```sh
npm install
```

### 3. Configure the `.env.local` File

Create a `.env.local` file in the `streamui` directory and add the following environment variables:

```env
VITE_API_BASE_URL=http://localhost:3001
```

Replace `http://localhost:3001` with the URL where your StreamAPI backend is running.

### 4. Start the Development Server

```sh
npm run dev
```

The UI will be available at `http://localhost:5173`.

### 5. Connect to the Backend

Ensure that your StreamAPI backend is running and that the `CORS_ORIGIN` in your `.env` file is set to `http://localhost:5173` to allow the UI to communicate with the backend.

```env
CORS_ORIGIN=http://localhost:5173
```

### 6. Access the UI

Open your browser and navigate to `http://localhost:5173` to access the StreamAPI user interface.

## Features

- Quick and easy video conversion to M3U8 format.
- Flask-based API for seamless integration.
- Customizable and extensible for your specific needs.

## Contributing

Feel free to open an issue or submit a pull request to improve StreamAPI!

## Task List

- [x] **User Authentication**: Implement a login system and integrate JSON Web Tokens (JWT) for secure API access.

- [ ] **Multiple Resolutions Support**: Enhance the API to handle multiple video resolutions, providing flexibility for different streaming scenarios.

- [ ] **Customize Output Format**: Allow users to specify custom output formats for converted videos.

- [ ] **Optimize FFMPEG Parameters**: Fine-tune FFMPEG parameters for better performance and efficiency.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.