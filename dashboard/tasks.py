import os
from datetime import datetime, timedelta

import pandas as pd
import six
from django.core.mail import EmailMessage, EmailMultiAlternatives
from google.cloud import translate_v2 as translate

from celery import shared_task
from common.reports import get_SWS_report
from dashboard.models import JGWCache
from events.logic.add_chapters_feedback_data import fetch_chapters_feedback_from_api_to_db
from events.logic.add_chapters_opened_data import fetch_chapters_opened_data_from_api_to_db
from events.logic.add_homepage_events_to_db import fetch_and_save_homepage_events_to_db
from events.logic.add_links_click_data import fetch_links_click_events_from_api_to_db
from events.logic.add_report_issue_events import fetch_report_issue_events_from_api_to_db
from events.logic.add_sws_pasi_data import fetch_sws_pasi_events_from_api_to_db
from events.logic.add_telephone_click import fetch_telephone_click_events_from_api_to_db
from events.logic.add_user_engagement_location_to_db import fetch_and_save_user_engagement_location_to_db
from help_contacts.logic.add_help_contacts_logic import fetch_help_contacts_from_api_to_db
from jgwpandas.settings import EMAIL_HOST_USER
import base64
import requests
from pipeline.models import CommandLog

from preference.logic.add_preferences_logic import fetch_preferences_from_api_to_db
from preference.tasks import attach_countries_to_state
from question.logic.add_inline_question_logic import fetch_inline_questions_from_api_to_db
from question.logic.add_messaging_question_logic import fetch_messaging_questions_from_api_to_db
from common.logger import KunfuPandaLogger

from dashboard.models import JGWCache

from email.mime.image import MIMEImage
import os
import mimetypes

client = translate.Client()


def translate_to_eng(text, client=client):
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    if isinstance(text, str):
        result = client.translate(text, target_language="en")
        return result["translatedText"]
    return text


def fetch_data_from_jgw_api():
    try:
        fetch_preferences_from_api_to_db()
        CommandLog.objects.create(
            command_name="add_preferences_from_api",
            data_fetch="Preferences",
            error="None",
            command_status=True,
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="add_preferences_from_api", data_fetch="Preferences", error=e, command_status=False
        )

    try:
        fetch_inline_questions_from_api_to_db()
        CommandLog.objects.create(
            command_name="add_inline_question_from_api",
            data_fetch="Inline questions",
            error="None",
            command_status=True,
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="add_inline_question_from_api",
            command_status=False,
            error=e,
            data_fetch="Inline questions",
        )

    try:
        fetch_messaging_questions_from_api_to_db()
        CommandLog.objects.create(
            command_name="add_messaging_question_from_api",
            data_fetch="Messsaging questions",
            error="None",
            command_status=True,
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="add_messaging_question_from_api",
            data_fetch="Messaging questions",
            error=e,
            command_status=False,
        )

    try:
        fetch_chapters_opened_data_from_api_to_db()
        CommandLog.objects.create(
            command_name="cache_bigquery_data - chapters_opened",
            data_fetch="Events",
            error="None",
            command_status=True,
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="cache_bigquery_data - chapters_opened",
            data_fetch="Events",
            error=e,
            command_status=False,
        )

    try:
        fetch_chapters_feedback_from_api_to_db()
        CommandLog.objects.create(
            command_name="cache_bigquery_data - chapters_feedback",
            data_fetch="Events",
            error="None",
            command_status=True,
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="cache_bigquery_data - chapters_feedback",
            data_fetch="Events",
            error=e,
            command_status=False,
        )

    try:
        fetch_sws_pasi_events_from_api_to_db()
        CommandLog.objects.create(
            command_name="cache_bigquery_data - sws_pasi_events",
            data_fetch="Events",
            error="None",
            command_status=True,
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="cache_bigquery_data - sws_pasi_events",
            data_fetch="Events",
            error=e,
            command_status=False,
        )

    try:
        fetch_help_contacts_from_api_to_db()
        CommandLog.objects.create(
            command_name="add_help_contacts_from_api",
            data_fetch="Help contacts",
            error="None",
            command_status=True,
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="add_help_contacts_from_api",
            data_fetch="Help contacts",
            error=e,
            command_status=False,
        )

    try:
        fetch_links_click_events_from_api_to_db()
        CommandLog.objects.create(
            command_name="add_link_clicks_data", data_fetch="Link clicks", error="None", command_status=True
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="add_link_clicks_data", data_fetch="Link clicks", error=e, command_status=False
        )

    try:
        fetch_telephone_click_events_from_api_to_db()
        CommandLog.objects.create(
            command_name="add_telephone_clicks_data",
            data_fetch="Telephone number clicks",
            error="None",
            command_status=True,
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="add_telephone_clicks_data",
            data_fetch="Telephone number clicks",
            error=e,
            command_status=False,
        )

    try:
        fetch_and_save_homepage_events_to_db()
        CommandLog.objects.create(
            command_name="add_homepage_events",
            data_fetch="Homepage events",
            error="None",
            command_status=True,
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="add_homepage_events", data_fetch="Homepage events", error=e, command_status=False
        )

    try:
        fetch_report_issue_events_from_api_to_db()
        CommandLog.objects.create(
            command_name="fetch_report_issue_events",
            data_fetch="Report Issue Events",
            error="None",
            command_status=True,
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="fetch_report_issue_events",
            data_fetch="Report Issue Events",
            error=e,
            command_status=False,
        )

    # should always come last
    try:
        attach_countries_to_state()
        CommandLog.objects.create(
            command_name="attach_countries_to_state",
            data_fetch="Country names",
            error="None",
            command_status=True,
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="attach_countries_to_state",
            data_fetch="Country names",
            error=e,
            command_status=False,
        )

    try:
        fetch_and_save_user_engagement_location_to_db()
        CommandLog.objects.create(
            command_name="add_user_engagement_location_to_db",
            data_fetch="User engagement location",
            error="None",
            command_status=True,
        )
    except Exception as e:
        CommandLog.objects.create(
            command_name="add_user_engagement_location_to_db",
            data_fetch="User engagement location",
            error=e,
            command_status=False,
        )

@shared_task(name="get_jgw_data")
def fetch_API_data():
    # fetch data from api v2
    fetch_data_from_jgw_api()


@shared_task(name="send_email_notification")
def send_email_notification(subject, message, attachment_path, recipients, html_message, inline_images):
    mail = EmailMultiAlternatives(subject, message, EMAIL_HOST_USER, recipients)
    if attachment_path:
        mail.attach_file(attachment_path)
    
    if html_message:
        mail.attach_alternative(html_message, "text/html")

    if inline_images:
        for cid, img_path in inline_images.items():
            if os.path.exists(img_path):
                mime_type, _ = mimetypes.guess_type(img_path)
                if not mime_type:
                    mime_type = "../static/logo.jpeg"

                with open(img_path, "rb") as img_file:
                    image = MIMEImage(img_file.read(), _subtype=mime_type.split("/")[-1])
                    image.add_header("Content-ID", f"<{cid}>")
                    image.add_header("Content-Disposition", "inline", filename=os.path.basename(img_path))
                    mail.attach(image)

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
        "Authorization": f"Basic {base64.b64encode((auth_api_username + ':' + auth_api_password).encode('utf-8')).decode('utf-8')}",
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
