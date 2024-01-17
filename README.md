# StreamAPI: FFMPEG API for Video Conversion

StreamAPI is a simple yet powerful FFMPEG-based API that allows you to effortlessly convert your videos into the widely used M3U8 format. With easy setup and execution, this tool streamlines the process of adapting your videos for various streaming applications.

## Getting Started

Follow these simple steps to get started with StreamAPI:

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

### 5. Set the `UPLOAD_FOLDER` and `JWT_SECRET_KEY` Variable

1. Open the newly renamed `.env` file and set the `UPLOAD_FOLDER` variable to the path where you want to save your converted videos.
2. Set your `JWT_SECRET_KEY` sentence

```env
UPLOAD_FOLDER=/path/to/your/upload/folder
JWT_SECRET_KEY=my_secret_key
```

Replace `/path/to/your/upload/folder` with the actual directory path where you want to store the converted videos.

### 6. Run the Flask Application

```bash
python app.py
```

That's it! Your StreamAPI server is now up and running. You can now utilize the API to convert your videos to the M3U8 format seamlessly.

## Usage

To convert a video, send a POST request to the appropriate endpoint with the video file. The API will handle the conversion process and provide you with the M3U8 file for streaming.

```bash
curl -X POST -F "file=@your_video.mp4" http://localhost:3001/v1/stream/app/upload
```

Make sure to replace `your_video.mp4` with the actual file path of the video you want to convert.

## Features

- Quick and easy video conversion to M3U8 format.
- Flask-based API for seamless integration.
- Customizable and extensible for your specific needs.

## Contributing

If you'd like to contribute to StreamAPI, please fork the repository and submit pull requests. Feel free to open issues for bug reports or feature requests.

## Task List

- [x] **User Authentication**: Implement a login system and integrate JSON Web Tokens (JWT) for secure API access.

- [ ] **Multiple Resolutions Support**: Enhance the API to handle multiple video resolutions, providing flexibility for different streaming scenarios.

- [ ] **Customize Output Format**: Allow users to specify custom output formats for converted videos.

- [ ] **Optimize FFMPEG Parameters**: Fine-tune FFMPEG parameters for better performance and efficiency.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

StreamAPI - Your go-to solution for effortless video conversion to M3U8!