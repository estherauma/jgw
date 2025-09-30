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

# Copy google_cred.json from BuildKit secret
RUN --mount=type=secret,id=google_cred,target=/tmp/google_cred.json \
    cp /tmp/google_cred.json /app/google_cred.json

RUN chown -R celery:celery /app

USER celery

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
