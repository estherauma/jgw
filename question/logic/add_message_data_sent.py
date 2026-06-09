from datetime import datetime, timedelta
import requests
import time
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
from question.logic.add_actual_message_sent_data import save_messages_to_db
from question.models import ActualMessageSent, MessageDataSent
from common.logger import KunfuPandaLogger
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.utils.date_utils import todays_date

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/message_data.log")

PAGE_SIZE = 1000
API_TIMEOUT_SECONDS = 60


class _MessageDataLookupCache:
    """In-memory cache for FK lookups within a fetch run."""

    def __init__(self):
        self._languages = {}
        self._destinations = {}
        self._origins = {}
        self._genders = {}
        self._ages = {}
        self._organisations = {}

    def get_language(self, language_code):
        if language_code not in self._languages:
            self._languages[language_code] = get_or_add_language_to_db(language_code)
        return self._languages[language_code]

    def get_destination(self, country_name):
        if country_name not in self._destinations:
            self._destinations[country_name] = get_or_add_country_to_db(
                country_name, source="destination"
            )
        return self._destinations[country_name]

    def get_origin(self, country_name):
        if country_name not in self._origins:
            self._origins[country_name] = get_or_add_country_to_db(country_name, source="origin")
        return self._origins[country_name]

    def get_gender(self, gender):
        if gender not in self._genders:
            self._genders[gender] = get_or_add_gender_to_db(gender)
        return self._genders[gender]

    def get_age(self, age_range):
        if age_range not in self._ages:
            self._ages[age_range] = get_or_add_age_to_db(age_range)
        return self._ages[age_range]

    def get_organisation(self, organisation_name):
        if organisation_name not in self._organisations:
            self._organisations[organisation_name] = get_or_add_organisation_to_db(organisation_name)
        return self._organisations[organisation_name]


def _parse_api_datetime(value):
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _api_bool(value, default=False):
    """Coerce API booleans; bulk_create does not apply model field defaults."""
    return default if value is None else value


def _get_fetch_date_range():
    latest_message = MessageDataSent.objects.order_by("-api_created_at").first()

    if latest_message:
        start_date = latest_message.api_created_at.date() + timedelta(days=1)
    else:
        start_date = datetime.strptime(APPLICATION_POSSIBLE_START_DATE, "%Y-%m-%d").date()

    end_date = datetime.strptime(todays_date(), "%Y-%m-%d").date()
    return start_date, end_date


def _fetch_page(url, headers, params, page_number, max_retries=3):
    """
    Fetches a single API page. Returns (data, pagination).
    Raises the last exception if all retries are exhausted.
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                delay = 2 ** attempt
                kunfu_panda_logger.info(f"⏳ Waiting {delay} seconds before retry...")
                time.sleep(delay)

            cursor_label = params.get("cursor") or "start"
            kunfu_panda_logger.info(
                f"  📦 Page {page_number} (cursor: {cursor_label}) - Attempt {attempt + 1}"
            )
            response = requests.get(url, headers=headers, params=params, timeout=API_TIMEOUT_SECONDS)
            response.raise_for_status()

            response_data = response.json()
            return response_data.get("data", []), response_data.get("pagination", {})

        except requests.exceptions.Timeout as exc:
            last_error = exc
            kunfu_panda_logger.warning(
                f"  ⏰ TIMEOUT: Page {page_number} timed out (attempt {attempt + 1})"
            )
        except requests.exceptions.RequestException as exc:
            last_error = exc
            kunfu_panda_logger.error(f"  🚫 API ERROR: {str(exc)} (attempt {attempt + 1})")

    kunfu_panda_logger.error(f"  ❌ FAILED: Max retries exceeded for page {page_number}")
    raise last_error


def _build_message_instance(message_data, cache, actual_messages_by_id):
    organisation = None
    if message_data.get("organisationCode"):
        organisation = cache.get_organisation(message_data["organisation"])

    message_id = message_data["messageId"]

    return MessageDataSent(
        message_id=message_id,
        message_content=actual_messages_by_id.get(message_id),
        message_title=message_data["messageTitle"],
        message_title_english=message_data["messageTitleEnglish"],
        message_date=_parse_api_datetime(message_data["messageDate"]),
        message_delivered_date=parse_date_or_none(message_data.get("messageDeliveredDate")),
        message_queued=_api_bool(message_data.get("messageQueued")),
        message_delivered=_api_bool(message_data.get("messageDelivered")),
        message_notification_sent_to_fcm=_api_bool(message_data.get("messageNotificationSentToFCM")),
        device_id=message_data["deviceId"],
        device_model=message_data["deviceModel"],
        app_id=message_data["appId"],
        app_version=message_data["appVersion"],
        registration_token=message_data.get("registrationToken", ""),
        language=cache.get_language(message_data["language"]),
        destination=cache.get_destination(message_data["destination"]),
        origin_country=cache.get_origin(message_data["locale"]),
        destination_state=message_data.get("destinationState", ""),
        immigration_status=message_data.get("immigrationStatus", ""),
        age=cache.get_age(message_data["age"]),
        gender=cache.get_gender(message_data["gender"]),
        seen_tab_welcome_text=message_data["seenTabWelcomeText"],
        organisation=organisation,
        factory_farm=message_data.get("factoryFarm", ""),
        user_created_at=_parse_api_datetime(message_data["userCreatedAt"]),
        user_updated_at=_parse_api_datetime(message_data["userUpdatedAt"]),
        api_created_at=_parse_api_datetime(message_data["createdAt"]),
        api_updated_at=_parse_api_datetime(message_data["updatedAt"]),
    )


def _store_page(page_data, cache):
    """
    Stores one API page using bulk_create with per-page FK prefetch.
    Falls back to individual saves if bulk_create fails.
    """
    if not page_data:
        return 0, 0

    message_ids = [message["messageId"] for message in page_data]
    actual_messages_by_id = {
        message.message_id: message
        for message in ActualMessageSent.objects.filter(message_id__in=message_ids)
    }

    instances = []
    failed_count = 0

    for message_data in page_data:
        try:
            instances.append(_build_message_instance(message_data, cache, actual_messages_by_id))
        except Exception as exc:
            failed_count += 1
            kunfu_panda_logger.error(
                f"  ❌ Error building message {message_data.get('messageId')}: {str(exc)}"
            )

    if not instances:
        return 0, failed_count

    try:
        with transaction.atomic():
            MessageDataSent.objects.bulk_create(instances, batch_size=len(instances))
        return len(instances), failed_count
    except Exception as exc:
        kunfu_panda_logger.warning(
            f"  ⚠️ bulk_create failed ({str(exc)}), falling back to individual saves"
        )

    stored_count = 0
    for instance in instances:
        try:
            with transaction.atomic():
                instance.save()
            stored_count += 1
        except Exception as exc:
            failed_count += 1
            kunfu_panda_logger.error(
                f"  ❌ Error saving message {instance.message_id}: {str(exc)}"
            )

    return stored_count, failed_count


def fetch_and_store_message_data_for_date_range(start_date_str, end_date_str, page_size=PAGE_SIZE):
    """
    Fetches and stores message analytics data page-by-page using cursor pagination.
    Each API page is written to the database before the next page is fetched.
    """
    page_size = min(page_size, PAGE_SIZE)
    url = f"{settings.MESSAGING_API_BASE_URL}/v1/message-analytics/events"
    headers = {"secret": settings.MESSAGING_API_SECRET}
    cache = _MessageDataLookupCache()

    cursor = None
    page_number = 1
    stored_count = 0
    failed_count = 0
    fetched_count = 0

    kunfu_panda_logger.info(f"📅 Fetching and storing: {start_date_str} to {end_date_str}")

    while True:
        params = {
            "pagination": "true",
            "limit": page_size,
            "startDate": f"{start_date_str} 00:00:00",
            "endDate": f"{end_date_str} 23:59:59",
        }
        if cursor:
            params["cursor"] = cursor

        try:
            page_data, pagination = _fetch_page(url, headers, params, page_number)
        except Exception:
            kunfu_panda_logger.error(
                f"  ❌ Stopping after page {page_number - 1}: {stored_count} stored so far"
            )
            break

        if page_data:
            fetched_count += len(page_data)
            page_stored, page_failed = _store_page(page_data, cache)
            stored_count += page_stored
            failed_count += page_failed
            kunfu_panda_logger.info(
                f"  ✅ Page {page_number}: fetched {len(page_data)}, "
                f"stored {page_stored}, failed {page_failed}"
            )
        else:
            kunfu_panda_logger.info(f"  📭 Page {page_number}: No more data")

        if not pagination.get("hasNextPage"):
            kunfu_panda_logger.info(f"  🏁 End of data for {start_date_str} to {end_date_str}")
            break

        cursor = pagination.get("nextCursor")
        if not cursor:
            break

        page_number += 1

    kunfu_panda_logger.info(
        f"📊 Completed {start_date_str} to {end_date_str}: "
        f"{fetched_count} fetched, {stored_count} stored, {failed_count} failed"
    )
    return stored_count, failed_count, fetched_count


def fetch_and_store_message_data():
    """
    Fetches message data for the remaining date range from API and stores in database.
    """
    kunfu_panda_logger.info("=" * 60)
    kunfu_panda_logger.info("🎯 STARTING COMPLETE MESSAGE DATA PROCESS")
    kunfu_panda_logger.info("=" * 60)

    kunfu_panda_logger.info("📝 Step 1: Saving actual messages...")
    actual_messages = save_messages_to_db()
    kunfu_panda_logger.info(f"✅ Step 1 Complete: Saved {actual_messages} actual messages")

    start_date, end_date = _get_fetch_date_range()

    if start_date > end_date:
        kunfu_panda_logger.info("📭 No new data to process - all caught up!")
        return 0

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    kunfu_panda_logger.info("📡 Step 2: Fetching and storing message data page-by-page...")
    kunfu_panda_logger.info(f"📅 Date Range: {start_date_str} to {end_date_str}")

    stored_count, failed_count, fetched_count = fetch_and_store_message_data_for_date_range(
        start_date_str, end_date_str
    )

    kunfu_panda_logger.info("=" * 60)
    kunfu_panda_logger.info("🎉 COMPLETE MESSAGE DATA PROCESS COMPLETED!")
    kunfu_panda_logger.info("📊 FINAL RESULTS:")
    kunfu_panda_logger.info(f"  📥 Total Fetched: {fetched_count} messages")
    kunfu_panda_logger.info(f"  ✅ Successfully Stored: {stored_count} messages")
    kunfu_panda_logger.info(f"  ❌ Failed: {failed_count} messages")
    if stored_count + failed_count > 0:
        success_rate = stored_count / (stored_count + failed_count) * 100
        kunfu_panda_logger.info(f"  📈 Success Rate: {success_rate:.1f}%")
    else:
        kunfu_panda_logger.info("  📈 Success Rate: N/A")
    kunfu_panda_logger.info("=" * 60)

    return stored_count
