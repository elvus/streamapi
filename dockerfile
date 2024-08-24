FROM --platform=linux/amd64 python:alpine

WORKDIR /app
COPY requirements.txt .
RUN apk add --no-cache ffmpeg
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5000
CMD ["python", "app.py"]