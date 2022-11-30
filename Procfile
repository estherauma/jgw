web: gunicorn jgwpandas.wsgi --log-file -
worker: celery -A jgwpandas worker --concurrency=2 --beat -l info