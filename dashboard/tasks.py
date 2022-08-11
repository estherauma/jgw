import glob
import os
from datetime import datetime, timedelta
from logging import getLogger

import pandas as pd
import six
from celery import shared_task
from django.core.mail import EmailMessage
from google.cloud import translate_v2 as translate
from jgwpandas.settings import EMAIL_HOST_USER

from dashboard.models import TranslatedQuestionText, TranslatedResponseText, TranslatedText
from dashboard.views import get_report

client = translate.Client()
debug_logger = getLogger("djangoDebug")


def translate_to_eng(text, client=client):
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    if isinstance(text, str):
        result = client.translate(text, target_language="en")
        return result["translatedText"]
    return text


@shared_task(name="get_jgw_data")
def fetch_API_data():
    from common.retrieve_data import JGWApi as APIHelper

    jgw_api = APIHelper()
    for key in [
        "inline",
        "preferences",
        "messaging",
        "help_contacts",
        "visa",
        "joboffer",
        "contract",
        "beforeyougo",
    ]:
        jgw_api.get_data(key=key)


@shared_task(name="translate_to_eng")
def translate_API_data():
    def _doer(model, limit=50):
        untranslated_text = model.objects.filter(translation__isnull=True)
        if untranslated_text.exists():
            objs = []
            for obj in untranslated_text[:limit]:
                obj.translation = translate_to_eng(obj.original_text)
                objs.append(obj)
            model.objects.bulk_update(objs, ["translation"])

    for model in [TranslatedQuestionText, TranslatedResponseText, TranslatedText]:
        _doer(model)


@shared_task(name="send_email_notification")
def send_email_notification(subject, message, attachment_path, recipients):
    mail = EmailMessage(subject, message, EMAIL_HOST_USER, recipients)
    mail.attach_file(attachment_path)
    mail.send()


@shared_task(name="generate_report")
def generate_report():
    today = datetime.today().strftime("%Y-%m-%d")
    week_number = int(datetime.today().strftime("%U"))
    if week_number % 2 == 0:
        return
    filename = get_report(start="2022-06-01", end=today, category="preferences")
    send_email_notification.delay(
        subject=f"{today}-SWS Report",
        message=f"Hello, \nPlease find attached the SWS Report for {datetime.today() - timedelta(weeks=2)} to {today}.\nJGW.Pandas",
        attachment_path=filename,
        recipients=[],
    )


@shared_task(name="_clean_data")
def clean_data(filename):
    from common.retrieve_data import JGWApi as APIHelper

    api_helper = APIHelper()
    others_path = filename.split(".csv")[0]
    df = pd.read_csv(filename)
    df = api_helper.clean_data(df)
    data = df.to_dict(orient="records")
    for f in glob.glob(f"{others_path}*.csv"):
        os.remove(f)
    api_helper.write_data_to_file(data, filename)


@shared_task(name="test_task")
def test_task():
    debug_logger.debug("Celery is working!")


@shared_task(name="send_email_notification")
def send_email_notification(subject, recipients, message, attachment_path):
    mail = EmailMessage(subject, message, EMAIL_HOST_USER, recipients)
    mail.attach_file(attachment_path)
    mail.send()
