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


def get_message_data_for_single_day(date_str, batch_size=5000, max_retries=3):
    """
    Fetches message analytics data for a single day in batches of 200.
    
    Args:
        date_str (str): Date in format "YYYY-MM-DD"
        batch_size (int): Number of records per batch (default: 200)
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        list: All message data records for the day
    """
    url = f"{settings.MESSAGING_API_BASE_URL}/v1/message-analytics/events"
    headers = {"secret": settings.MESSAGING_API_SECRET}
    
    all_messages = []
    offset = 0
    batch_number = 1
    
    kunfu_panda_logger.info(f"📅 Fetching data for date: {date_str}")
    
    while True:
        params = {
            "startDate": f"{date_str} 00:00:00",
            "endDate": f"{date_str} 23:59:59",
            "limit": batch_size,
            "offset": offset
        }
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = 2 ** attempt
                    kunfu_panda_logger.info(f"⏳ Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                
                kunfu_panda_logger.info(f"  📦 Batch {batch_number} (offset: {offset}) - Attempt {attempt + 1}")
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                
                response_data = response.json()
                data = response_data.get("data", [])
                
                if data:
                    all_messages.extend(data)
                    kunfu_panda_logger.info(f"  ✅ Batch {batch_number}: {len(data)} records fetched")
                else:
                    kunfu_panda_logger.info(f"  📭 Batch {batch_number}: No more data")
                
                break
                
            except requests.exceptions.Timeout:
                kunfu_panda_logger.warning(f"  ⏰ TIMEOUT: Batch {batch_number} timed out (attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    kunfu_panda_logger.error(f"  ❌ FAILED: Max retries exceeded for batch {batch_number}")
                    return all_messages
            except requests.exceptions.RequestException as e:
                kunfu_panda_logger.error(f"  🚫 API ERROR: {str(e)} (attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    kunfu_panda_logger.error(f"  ❌ FAILED: Max retries exceeded for batch {batch_number}")
                    return all_messages
            except Exception as e:
                kunfu_panda_logger.error(f"  💥 UNEXPECTED ERROR: {str(e)} (attempt {attempt + 1})")
                return all_messages
        
        if len(data) < batch_size:
            kunfu_panda_logger.info(f"  🏁 End of data for {date_str}: {len(data)} records (less than batch size {batch_size})")
            break
        
        offset += batch_size
        batch_number += 1
        
        time.sleep(1)
    
    kunfu_panda_logger.info(f"📊 Date {date_str} completed: {len(all_messages)} total records")
    return all_messages


def get_message_data_from_api():
    """
    Fetches message analytics data from the JGW API for all remaining days.
    Processes each day separately but in a single command execution.
    """
    
    latest_message = MessageDataSent.objects.order_by("-api_created_at").first()
    
    if latest_message:
        start_date = latest_message.api_created_at.date() + timedelta(days=1)
    else:
        start_date = datetime.strptime(APPLICATION_POSSIBLE_START_DATE, "%Y-%m-%d").date()
    
    end_date = datetime.strptime(todays_date(), "%Y-%m-%d").date()
    
    if start_date > end_date:
        kunfu_panda_logger.info("🎉 All data is up to date! No new days to process.")
        return []
    
    total_days = (end_date - start_date).days + 1
    kunfu_panda_logger.info(f"🚀 STARTING BATCH PROCESSING")
    kunfu_panda_logger.info(f"📅 Date Range: {start_date} to {end_date}")
    kunfu_panda_logger.info(f"📊 Total Days to Process: {total_days}")
    
    all_messages = []
    successful_days = 0
    failed_days = 0
    current_date = start_date
    day_number = 1
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        kunfu_panda_logger.info(f"🗓️  Processing Day {day_number}/{total_days}: {date_str}")
        
        try:
            day_messages = get_message_data_for_single_day(date_str, batch_size=5000)
            
            if day_messages:
                all_messages.extend(day_messages)
                successful_days += 1
                kunfu_panda_logger.info(f"✅ Day {day_number} completed: {len(day_messages)} records")
            else:
                kunfu_panda_logger.info(f"📭 Day {day_number}: No data found")
                successful_days += 1
            
        except Exception as e:
            failed_days += 1
            kunfu_panda_logger.error(f"❌ Day {day_number} failed: {str(e)}")
        
        current_date += timedelta(days=1)
        day_number += 1
        
        if current_date <= end_date:
            kunfu_panda_logger.info(f"⏳ Waiting 2 seconds before next day...")
            time.sleep(2)
    
    kunfu_panda_logger.info("🎉 ALL DAYS PROCESSING COMPLETED!")
    kunfu_panda_logger.info(f"📊 FINAL SUMMARY:")
    kunfu_panda_logger.info(f"  📅 Total Days Processed: {total_days}")
    kunfu_panda_logger.info(f"  ✅ Successful Days: {successful_days}")
    kunfu_panda_logger.info(f"  ❌ Failed Days: {failed_days}")
    kunfu_panda_logger.info(f"  📊 Total Records Fetched: {len(all_messages)}")
    
    return all_messages


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
        try:
            message_content = ActualMessageSent.objects.get(message_id=message_data["messageId"])
        except ActualMessageSent.DoesNotExist:
            message_content = None

        message = MessageDataSent.objects.create(
            message_id=message_data["messageId"],
            message_content=message_content,
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
    Fetches message data for all remaining days from API and stores in database.
    Processes each day separately but in a single command execution.
    """
    kunfu_panda_logger.info("=" * 60)
    kunfu_panda_logger.info("🎯 STARTING COMPLETE MESSAGE DATA PROCESS")
    kunfu_panda_logger.info("=" * 60)
    
    kunfu_panda_logger.info("📝 Step 1: Saving actual messages...")
    actual_messages = save_messages_to_db()
    kunfu_panda_logger.info(f"✅ Step 1 Complete: Saved {actual_messages} actual messages")
    
    kunfu_panda_logger.info("📡 Step 2: Fetching message data for all remaining days...")
    messages = get_message_data_from_api()
    
    if not messages:
        kunfu_panda_logger.info("📭 No new data to process - all caught up!")
        return 0
    
    kunfu_panda_logger.info(f"✅ Step 2 Complete: Fetched {len(messages)} total message records")
    
    kunfu_panda_logger.info("💾 Step 3: Storing all messages in database...")
    stored_count = 0
    failed_count = 0
    
    chunk_size = 100 
    total_chunks = (len(messages) + chunk_size - 1) // chunk_size
    
    for i in range(0, len(messages), chunk_size):
        chunk = messages[i:i + chunk_size]
        chunk_number = i // chunk_size + 1
        
        kunfu_panda_logger.info(f"  💾 Processing Database Chunk {chunk_number}/{total_chunks} ({len(chunk)} messages)")
        
        for message_data in chunk:
            try:
                message, created = store_message_data(message_data)
                if created:
                    stored_count += 1
            except Exception as e:
                failed_count += 1
                kunfu_panda_logger.error(f"  ❌ Error processing message {message_data.get('messageId')}: {str(e)}")
                continue
        
        kunfu_panda_logger.info(f"  ✅ Chunk {chunk_number} Complete: {stored_count} stored, {failed_count} failed so far")

    kunfu_panda_logger.info("=" * 60)
    kunfu_panda_logger.info("🎉 COMPLETE MESSAGE DATA PROCESS COMPLETED!")
    kunfu_panda_logger.info(f"📊 FINAL RESULTS:")
    kunfu_panda_logger.info(f"  ✅ Successfully Stored: {stored_count} messages")
    kunfu_panda_logger.info(f"  ❌ Failed: {failed_count} messages")
    kunfu_panda_logger.info(f"  📈 Success Rate: {(stored_count / (stored_count + failed_count) * 100):.1f}%" if (stored_count + failed_count) > 0 else "  📈 Success Rate: N/A")
    kunfu_panda_logger.info("=" * 60)
    
    return stored_count
