FROM --platform=linux/amd64 python:alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV UPLOAD_FOLDER=/app/uploads
ENV JWT_SECRET_KEY=secret
ENV PORT=5000
EXPOSE 5000
CMD ["python", "app.py"]