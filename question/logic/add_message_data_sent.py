from datetime import datetime
import requests
from django.conf import settings
from django.db import transaction

from common.helpers.model_helpers.preference import (
    get_or_add_age_to_db,
    get_or_add_country_to_db,
    get_or_add_gender_to_db,
    get_or_add_language_to_db,
    get_or_add_organisation_to_db,
    parse_date_or_none,
)
from question.models import MessageDataSent
from common.logger import KunfuPandaLogger
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.utils.date_utils import todays_date

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/message_data.log")


def get_message_data_from_api():
    """
    Fetches message analytics data from the JGW API
    """
    latest_message = MessageDataSent.objects.order_by("-api_created_at").first()
    start_date = (
        latest_message.api_created_at.strftime("%Y-%m-%d %H:%M:%S")
        if latest_message
        else APPLICATION_POSSIBLE_START_DATE
    )
    end_date = todays_date()

    url = f"{settings.MESSAGING_API_BASE_URL}/v1/message-analytics/events"
    headers = {"secret": settings.MESSAGING_API_SECRET}
    params = {"startDate": start_date, "endDate": end_date}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(len(response.json()["data"]))
        return response.json()["data"]
    except Exception as e:
        kunfu_panda_logger.error(f"Error fetching message data: {str(e)}")
        return []


@transaction.atomic
def store_message_data(message_data):
    """
    Stores a single message data record in the database
    """
    try:
        language_data = get_or_add_language_to_db(message_data["language"])
        destination_data = get_or_add_country_to_db(message_data["destination"], source="destination")
        origin_data = get_or_add_country_to_db(message_data["locale"], source="origin")
        gender_data = get_or_add_gender_to_db(message_data["gender"])
        age_data = get_or_add_age_to_db(message_data["age"])

        organisation = None
        if message_data.get("organisationCode"):
            organisation = get_or_add_organisation_to_db(message_data["organisation"])

        message_date = datetime.fromisoformat(message_data["messageDate"].replace("Z", "+00:00"))
        user_created_at = datetime.fromisoformat(message_data["userCreatedAt"].replace("Z", "+00:00"))
        user_updated_at = datetime.fromisoformat(message_data["userUpdatedAt"].replace("Z", "+00:00"))
        message_delivered_date = parse_date_or_none(message_data.get("messageDeliveredDate"))

        message = MessageDataSent.objects.create(
            message_id=message_data["messageId"],
            message_title=message_data["messageTitle"],
            message_title_english=message_data["messageTitleEnglish"],
            message_date=message_date,
            message_delivered_date=message_delivered_date,
            message_queued=message_data.get("messageQueued"),
            message_delivered=message_data.get("messageDelivered"),
            message_notification_sent_to_fcm=message_data.get("messageNotificationSentToFCM"),
            device_id=message_data["deviceId"],
            device_model=message_data["deviceModel"],
            app_id=message_data["appId"],
            app_version=message_data["appVersion"],
            registration_token=message_data.get("registrationToken", ""),
            language=language_data,
            destination=destination_data,
            origin_country=origin_data,
            destination_state=message_data.get("destinationState", ""),
            immigration_status=message_data.get("immigrationStatus", ""),
            age=age_data,
            gender=gender_data,
            seen_tab_welcome_text=message_data["seenTabWelcomeText"],
            organisation=organisation,
            factory_farm=message_data.get("factoryFarm", ""),
            user_created_at=user_created_at,
            user_updated_at=user_updated_at,
            api_created_at=message_data["createdAt"],
            api_updated_at=message_data["updatedAt"],
        )

        return message, True
    except Exception as e:
        kunfu_panda_logger.error(f"Error storing message data: {str(e)}")
        raise


def fetch_and_store_message_data():
    """
    Fetches message data from API and stores in database
    """
    messages = get_message_data_from_api()
    stored_count = 0

    for message_data in messages:
        try:
            message, created = store_message_data(message_data)
            if created:
                stored_count += 1
        except Exception as e:
            kunfu_panda_logger.error(f"Error processing message {message_data.get('messageId')}: {str(e)}")
            continue

    kunfu_panda_logger.info(f"Successfully stored {stored_count} new messages")
    return stored_count
