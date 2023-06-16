from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jgwpandas.settings")
celery_app = Celery("jgwpandas")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    "fetch-API-data": {
        "task": "get_jgw_data",
        "schedule": crontab(minute=0, hour=0),  # everyday at midnight
    },
    "cache_bigquery_data": {
        "task": "cache_bigquery_data",
        "schedule": crontab(minute=0, hour=0),  # everyday at midnight
    },
    "load_bigquery_data_once": {
        "task": "load_bigquery_data_once",
        "schedule": crontab(minute=0, hour=23) ,  # run 11pm everyday
    },
    "translate-API-data": {
        "task": "translate_to_eng",
        "schedule": crontab(minute="*/5"),  # every five minutes
    },
    "generate-report": {
        "task": "generate_report",
        "schedule": crontab(minute="0", hour="0", day_of_week="friday"),
    },
    "notify_admins_inactive_users": {
        "task": "notify_admins_inactive_users",
        "schedule": crontab(minute="0", hour="0", day_of_week="sunday"),
    },
}
