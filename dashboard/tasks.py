import os
from datetime import datetime, timedelta

import pandas as pd
import six
from celery import shared_task
from django.core.mail import EmailMessage
from google.cloud import translate_v2 as translate
from jgwpandas.settings import EMAIL_HOST_USER

from dashboard.models import JGWCache, TranslatedQuestionText, TranslatedResponseText, TranslatedText
from dashboard.views import get_report

client = translate.Client()


def translate_to_eng(text, client=client):
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    if isinstance(text, str):
        result = client.translate(text, target_language="en")
        return result["translatedText"]
    return text


@shared_task(name="get_jgw_data")
def fetch_API_data(category=None):
    from common.retrieve_data import JGWApi as APIHelper

    jgw_api = APIHelper()
    if category is not None:
        jgw_api.get_data(key=category)
        return

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
    if attachment_path:
        mail.attach_file(attachment_path)
    mail.send()


@shared_task(name="generate_report")
def generate_report():
    today = datetime.today().strftime("%Y-%m-%d")
    subject = f"{today}-SWS Report"
    message = f"Hello, \nPlease find attached the SWS Report for {datetime.today() - timedelta(weeks=2)} to {today}.\nJGW.Pandas"
    recipients = os.getenv("RECIPIENTS").split(" ")
    if recipients:
        filename = get_report(start="2022-06-01", end=today, category="preferences")
        attachment_path = filename
        mail = EmailMessage(subject, message, EMAIL_HOST_USER, recipients)
        mail.attach_file(attachment_path)
        mail.send()


@shared_task(name="_clean_data")
def clean_data(category):
    from common.retrieve_data import JGWApi as APIHelper

    api_helper = APIHelper()
    result = JGWCache.objects.filter(category=category, date_created=datetime.today().date()).first()
    df = pd.read_json(result.data, orient="records")
    df = api_helper.clean_data(df)
    data = df.to_json(orient="records")
    result.data = data
    result.is_cleaned = True
    result.save()
