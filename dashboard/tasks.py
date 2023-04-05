import os
from datetime import datetime, timedelta
import logging

import pandas as pd
import six
from django.core.mail import EmailMessage
from google.cloud import translate_v2 as translate

from celery import shared_task
from common.reports import get_SWS_report
from dashboard.models import JGWCache, TranslatedQuestionText, TranslatedResponseText, TranslatedText
from jgwpandas.settings import EMAIL_HOST_USER

client = translate.Client()
logger = logging.getLogger(__name__)

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
        "chapter_feedback",
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
    reports = ("preferences", "chapters", "inlineQNs_participation", "inlineQNs_responses")
    end = datetime.today().strftime("%Y-%m-%d")
    subject = f"{end}-SWS Report"
    message = f"Hello, \nPlease find attached the SWS Report for {datetime.today() - timedelta(weeks=2)} to {end}.\nJGW.Pandas"
    recipients = os.getenv("RECIPIENTS").split(" ")
    if recipients:
        attachments = [get_SWS_report(start="2022-06-01", end=end, category=f) for f in reports]
        mail = EmailMessage(subject, message, EMAIL_HOST_USER, recipients)
        for filename in attachments:
            mail.attach_file(filename)
        mail.send()


@shared_task(name="_clean_data")
def clean_data(category):
    from common.retrieve_data import JGWApi as APIHelper

    api_helper = APIHelper()
    result = JGWCache.objects.filter(category=category, date_created=datetime.today().date()).first()
    df = pd.read_json(result.data, orient="records")

    logger.info("-------before cleaning------")
    logger.info(df["gender"])
    df = api_helper.clean_data(df)
    logger.info(df["gender"])
    logger.info("------after cleaning------")

    data = df.to_json(orient="records")
    result.data = data
    result.is_cleaned = True
    result.save()
    return
