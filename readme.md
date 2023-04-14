# JGW Pandas

This repository contains code for running analytics on data collected by the JGW API

> Built with [Django](https://www.djangoproject.com/) and [UBold](https://coderthemes.com/ubold/)

## SetUp

   Follow the attached links to ensure the following are installed and running:

- [python](https://www.python.org/downloads/)
- [postgresql](https://www.postgresql.org/download/)
- [redis](https://redis.io/docs/getting-started/)

### Steps

1. Use [env.example](./env.example) as a template for your `.env` file where you can update any env variables such as db credentials.

   You can get an API key for the google service account from this [link](https://console.cloud.google.com/iam-admin/serviceaccounts/details/104736138538665133501/keys?project=just-good-work). Download the json file to the project root and rename it to `google_cred.json`

1. Set up your local database

   ```bash
   psql -U postgres -h 127.0.0.1 -f create_dev_db.sql
   ```

1. In the root directory, create a new virtual environment; activate it and install dependencies

   ```bash
   python3 -m venv ./.venv
   source ./.venv/bin/activate
   pip install -r requirements.txt
   ```

1. Run database migrations and collect static files with:

   These only need to be run when there's a change to the database structure or new assets/static files are added for the UI.
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

1. Run the following commands to start the celery scheduler and Django development server.

   ```bash
   # run celery worker and beat scheduler in background
   celery -A jgwpandas beat -l info --logfile=./celery/celery.beat.log --detach
   celery -A jgwpandas worker -l info --logfile=./celery/celery.log --detach

   #run this and follow the prompts to create a superuser account
   python manage.py createsuperuser

   # run dev-server and visit http://localhost:8000/ in the browser to use the app
   python manage.py runserver
   ```

   > NOTE: Accounts created through the Sign-Up page currently need to be activated by an admin user.

1. Use `CTRL+C` to terminate the django server.

   To stop the background celery services started in the step above, run the following command

   ```bash
   kill -9 $(ps aux | grep celery | grep -v grep | awk '{print $2}' | tr '\n'  ' ') > /dev/null 2>&1
   ```

## Testing

To run tests, run `coverage run manage.py test`   
To get coverage report, run `coverage report`
