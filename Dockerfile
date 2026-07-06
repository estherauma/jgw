# syntax=docker/dockerfile:1.6
FROM python:3.9-slim

RUN addgroup --system celery && adduser --system --ingroup celery celery

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    gettext \   
    python3-dev \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install --no-cache-dir --timeout=60 --retries=5 -r requirements.txt

COPY . /app/

# Create google_cred.json from base64 encoded secret
ARG GOOGLE_CREDENTIALS_BASE64
RUN echo "$GOOGLE_CREDENTIALS_BASE64" | base64 -d > /app/google_cred.json && \
    echo "Google credentials file created from base64" && \
    ls -la /app/google_cred.json

# Set Google Application Credentials environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/google_cred.json

RUN chown -R celery:celery /app

USER celery

EXPOSE 8000

CMD ["gunicorn", "jgwpandas.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
