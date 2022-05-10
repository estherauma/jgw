from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jgwpandas.settings")
celery_app = Celery("jgwpandas")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()


@celery_app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


celery_app.conf.beat_schedule = {
    "fetch-API-data": {
        "task": "get_jgw_data",
        "schedule": crontab(minute=0, hour=0),
    }
}
