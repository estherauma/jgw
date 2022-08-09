web: gunicorn jgwpandas.wsgi --log-file -
worker: celery -A jgwpandas worker -l info
beat: celery -A jgwpandas beat -l info