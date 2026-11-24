FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV SITE=https://YOUR-DOMAIN
RUN python build_pages.py
ENV PORT=7860
CMD gunicorn -b 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 300 app:app
