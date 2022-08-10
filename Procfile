web: gunicorn jgwpandas.wsgi --log-file -
worker: celery -A jgwpandas worker --beat -l info