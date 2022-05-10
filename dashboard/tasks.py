from __future__ import absolute_import, unicode_literals

from celery import shared_task
from common.retrieve_data import JGWApi as APIHelper

jgw_api = APIHelper()


@shared_task(name="get_jgw_data")
def fetch_API_data():
    for key in ["inline", "preferences", "messaging"]:
        jgw_api.get_data(key=key)
