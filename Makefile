.PHONY: celery-start celery-stop celery-restart format-redis add_genders runserver

celery-start:
	celery -A jgwpandas beat -l info --logfile=./celery/celery.beat.log --detach
	celery -A jgwpandas worker -l info --logfile=./celery/celery.log --detach

celery-stop:
	kill -9 $$(ps aux | grep celery | grep -v grep | awk '{print $$2}' | tr '\n'  ' ') > /dev/null 2>&1

format-redis:
	redis-cli flushdb

celery-restart: format-redis celery-start

add_genders:
	python manage.py add_genders

runserver:
	python manage.py runserver

runtests:
	coverage run manage.py test
