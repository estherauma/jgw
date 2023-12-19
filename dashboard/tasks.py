import os
from datetime import datetime, timedelta

import pandas as pd
import six
from django.core.mail import EmailMessage
from google.cloud import translate_v2 as translate

from celery import shared_task
from common.reports import get_SWS_report
from dashboard.management.commands.add_contacts import add_new_contacts
from dashboard.management.commands.add_genders import add_new_genders
from dashboard.models import JGWCache, TranslatedQuestionText, TranslatedResponseText, TranslatedText
from events.logic.add_chapters_feedback_data import fetch_chapters_feedback_from_api_to_db
from events.logic.add_chapters_opened_data import fetch_chapters_opened_data_from_api_to_db
from events.logic.add_links_click_data import fetch_links_click_events_from_api_to_db
from events.logic.add_sws_pasi_data import fetch_sws_pasi_events_from_api_to_db
from help_contacts.logic.add_help_contacts_logic import fetch_help_contacts_from_api_to_db
from jgwpandas.settings import EMAIL_HOST_USER
import base64
import requests
import json

from preference.logic.add_preferences_logic import fetch_preferences_from_api_to_db
from preference.tasks import attach_countries_to_state
from question.logic.add_inline_question_logic import fetch_inline_questions_from_api_to_db
from question.logic.add_messaging_question_logic import fetch_messaging_questions_from_api_to_db
from common.logger import KunfuPandaLogger

from dashboard.models import JGWCache

client = translate.Client()


def translate_to_eng(text, client=client):
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    if isinstance(text, str):
        result = client.translate(text, target_language="en")
        return result["translatedText"]
    return text


def fetch_data_from_jgw_api():
    fetch_preferences_from_api_to_db()
    fetch_inline_questions_from_api_to_db()
    fetch_messaging_questions_from_api_to_db()

    fetch_chapters_opened_data_from_api_to_db()
    fetch_chapters_feedback_from_api_to_db()
    fetch_sws_pasi_events_from_api_to_db()

    fetch_help_contacts_from_api_to_db()

    fetch_links_click_events_from_api_to_db()

    # should always come last
    attach_countries_to_state()


@shared_task(name="get_jgw_data")
def fetch_API_data():
    # fetch data from api v2
    fetch_data_from_jgw_api()


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
    df = api_helper.clean_data(df)
    if df is not None:
        data = df.to_json(orient="records")
        result.data = data
        result.is_cleaned = True
        result.save()
    return


@shared_task(name="fetch_summerberry_data")
def summerberry_data():
    logger = KunfuPandaLogger(log_file="logs/summerberry-api.log")
    logger.info(f"Date time: {datetime.now()} - Starting data fetch")
    auth_api_username = os.getenv("SUMMERBERRY_API_USERNAME")
    auth_api_password = os.getenv("SUMMERBERRY_API_PASSWORD")
    auth_api_url = os.getenv("SUMMERBERRY_API_URL")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Basic "
        + base64.b64encode((auth_api_username + ":" + auth_api_password).encode("utf-8")).decode("utf-8"),
    }
    response = requests.get(auth_api_url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Date time: {datetime.now()} - Error: {response.text}")
        return
    # create or update jgw cache
    JGWCache.objects.update_or_create(
        category="summerberry",
        date_created=datetime.today().date(),
        defaults={"data": response.json(), "is_cleaned": True},
    )
    logger.info(f"Date time: {datetime.now()} - Ending data fetch")
    return
