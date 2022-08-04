web: gunicorn jgwpandas.wsgi --log-file -
main_worker: celery -A jgwpandas worker -l info --logfile=./celery.log --beat