FROM --platform=linux/amd64 python:3.11-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache gcc musl-dev linux-headers ffmpeg \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]