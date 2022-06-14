# JGW Pandas

This repository contains code for running analytics on data collected by the JGW API

> [UI Template](https://colorlib.com/wp/template/bootstrap-sidebar-05/)
> Built with Django 

## SetUp

#### Pre-requisites 

- [python](https://www.python.org/downloads/)
- [postgresql](https://www.postgresql.org/download/)
- [redis](https://redis.io/docs/getting-started/)

#### Steps

1. Set up your local database

   Use [env.example](./env.example) as a template for your `.env` file where you can update any env variables such as db credentials.
   
   You can get an API key for the google service account from this [link](https://console.cloud.google.com/iam-admin/serviceaccounts/details/102058899159157121490/keys?project=pandas50eight). Download the json file to the project root and rename it to `google_cred.json`

```bash
psql -U postgres -h 127.0.0.1 -f create_dev_db.sql
```

2. In the root directory, create a new virtual environment; activate it and install dependencies

```bash
python3 -m venv ./.venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

3. run database migrations with:

```bash
python manage.py migrate
```

4. Run the following commands to start the celery scheduler and Django development server.

   Visit http://localhost:8000/ to use the running application

```bash
# run celery worker and beat scheduler in background
celery -A jgwpandas beat -l info --logfile=./celery/celery.beat.log --detach
celery -A jgwpandas worker -l info --logfile=./celery/celery.log --detach

# run django development server
python manage.py runserver
```

5. Use `CTRL+C` to terminate the django server. 

   To stop the background celery services started in the step above, run the following command

```bash
kill -9 $(ps aux | grep celery | grep -v grep | awk '{print $2}' | tr '\n'  ' ') > /dev/null 2>&1
````

