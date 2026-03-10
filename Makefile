.PHONY: celery-start celery-stop celery-restart format-redis add_genders runserver makemessages compilemessages

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

makemessages:
	python manage.py makemessages -l en_US -l es_ES

compilemessages:
	python manage.py compilemessages

export-cms:
	python manage.py export_cms_labels
	
docker_migrate:
	docker-compose -f docker-compose.dev.yml exec web python manage.py migrate

docker_makemigrations:
	docker-compose -f docker-compose.dev.yml exec web python manage.py makemigrations

docker_up:
	docker compose -f docker-compose.dev.yml up --build

docker_down:
	docker compose -f docker-compose.dev.yml down
	
docker_restart_web:
	docker compose -f docker-compose.dev.yml restart web