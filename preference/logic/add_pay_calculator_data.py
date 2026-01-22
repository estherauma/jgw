import requests
from datetime import datetime
from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.conf import settings
from preference.models import PayCalculator, Preference, OrganisationData
from common.logger import KunfuPandaLogger
from common.helpers.model_helpers.preference import (
    get_or_add_age_to_db,
    get_or_add_gender_to_db,
    get_or_add_immigration_status_to_db,
    get_or_add_country_to_db,
    get_or_add_country_state_to_db,
    get_or_add_organisation_to_db,
    get_or_add_organisation_access_code,
    get_or_add_factory_farm_to_db,
    add_sector_of_work_to_db,
    add_original_sector_of_work_to_db,
)

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/pay_calculator_tasks.log")


def parse_datetime_safe(date_str):
    """Safely parse datetime string from API response"""
    if not date_str:
        return None
    try:
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        return parse_datetime(date_str)
    except (ValueError, TypeError) as e:
        kunfu_panda_logger.warning(f"Failed to parse datetime '{date_str}': {str(e)}")
        return None


@transaction.atomic
def store_pay_calculator_data(calculator_data):
    """
    Stores a single pay calculator data record in the database.
    
    Args:
        calculator_data (dict): Pay calculator data from API response
        
    Returns:
        tuple: (PayCalculator instance, created boolean)
    """
    try:
        device_id = calculator_data.get("deviceId", "")
        api_created_at = parse_datetime_safe(calculator_data.get("createdAt"))
        
        if not device_id or not api_created_at:
            kunfu_panda_logger.warning("Missing deviceId or createdAt in calculator data, skipping")
            return None, False
        
        existing = PayCalculator.objects.filter(
            device_id=device_id,
            api_created_at=api_created_at
        ).first()
        if existing:
            kunfu_panda_logger.debug(f"Pay calculator record for device {device_id} at {api_created_at} already exists, skipping")
            return existing, False

        api_updated_at = parse_datetime_safe(calculator_data.get("updatedAt")) or api_created_at

        age_data = get_or_add_age_to_db(calculator_data.get("age"))
        gender_data = get_or_add_gender_to_db(calculator_data.get("gender"))
        immigration_status_data = get_or_add_immigration_status_to_db(calculator_data.get("immigrationStatus"))
        origin_data = get_or_add_country_to_db(calculator_data.get("locale"), source="locale")
        destination_data = get_or_add_country_to_db(calculator_data.get("destination"), source="destination")
        destination_state_data = get_or_add_country_state_to_db(calculator_data.get("destinationState"))
        
        organisation_data = None
        organisation_code = calculator_data.get("organisationCode")
        if organisation_code:
            try:
                organisation_data = OrganisationData.objects.get(org_code=organisation_code)
            except OrganisationData.DoesNotExist:
                organisation_data = OrganisationData.objects.get(name="ONS")
        
        organisation_access_code_data = get_or_add_organisation_access_code(calculator_data.get("organisationAccessCode"))
        factory_farm_data = get_or_add_factory_farm_to_db(calculator_data.get("factoryFarm"))
        
        preference = None
        if device_id:
            preference = Preference.objects.filter(device_id=device_id).order_by('-api_created_at').first()
        
        totals = calculator_data.get("totals", {})
        total_left = totals.get("totalLeft") if totals else None
        tax_reclaim = totals.get("taxReclaim") if totals else None
        
        panels = calculator_data.get("panels", {})
        estimated_pay = panels.get("estimatedPay", {})
        estimated_cost = panels.get("estimatedCost", {})
        
        pay_calculator = PayCalculator.objects.create(
            device_id=device_id,
            preference=preference,
            age=age_data,
            gender=gender_data,
            immigration_status=immigration_status_data,
            origin=origin_data,
            destination=destination_data,
            destination_state=destination_state_data,
            organisation=organisation_data,
            organisation_access_code=organisation_access_code_data,
            factory_farm=factory_farm_data,
            total_left=total_left,
            tax_reclaim=tax_reclaim,
            total_estimated_pay=estimated_pay.get("total"),
            weeks_worked=estimated_pay.get("weeksWorked"),
            income_tax=estimated_pay.get("incomeTax"),
            national_insurance=estimated_pay.get("nationalInsurance"),
            average_week_hours=estimated_pay.get("averageWeekHours"),
            total_estimated_cost=estimated_cost.get("total"),
            accomadation_per_week=estimated_cost.get("accommodationPerWeek"),
            transportation_within_uk=estimated_cost.get("transportationWithinUK"),
            visa_appointment_one_off=estimated_cost.get("visaAppointmentOneOff"),
            travel_home_to_uk_one_off=estimated_cost.get("travelHomeToUKOneOff"),
            food_per_week=estimated_cost.get("foodPerWeek"),
            api_created_at=api_created_at,
            api_updated_at=api_updated_at,
        )
        
        sectors_list = calculator_data.get("sectors", [])
        if sectors_list:
            sector_of_work_list = add_sector_of_work_to_db(sectors_list)
            pay_calculator.sectors_of_work.set(sector_of_work_list)
            original_sector_list = add_original_sector_of_work_to_db(sectors_list)
            pay_calculator.sectors.set(original_sector_list)
        
        kunfu_panda_logger.debug(f"Successfully stored pay calculator record for device {device_id}")
        return pay_calculator, True
        
    except Exception as e:
        kunfu_panda_logger.error(f"Error storing pay calculator data for {calculator_data.get('deviceId', 'unknown')}: {str(e)}")
        raise


def fetch_pay_calculator_data_from_api():
    """
    Fetches pay calculator data from the JGW API.
    
    Returns:
        list: List of pay calculator data records
    """
    url = f"{settings.JGW_API}pay-calculator"
    headers = {"secret": settings.JGW_API_SECRET}
    
    try:
        kunfu_panda_logger.info(f"Fetching pay calculator data from {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("status") != "OK":
            kunfu_panda_logger.warning(f"API returned non-OK status: {result.get('status')}")
            return []
        
        data = result.get("data", [])
        kunfu_panda_logger.info(f"Successfully fetched {len(data)} pay calculator records")
        return data
        
    except requests.exceptions.RequestException as e:
        kunfu_panda_logger.error(f"Error fetching pay calculator data: {str(e)}")
        raise
    except Exception as e:
        kunfu_panda_logger.error(f"Unexpected error fetching pay calculator data: {str(e)}")
        raise


def fetch_and_store_pay_calculator_data():
    """
    Fetches pay calculator data from API and stores in database.
    Processes data in chunks for better performance.
    
    Returns:
        int: Number of new records stored
    """
    kunfu_panda_logger.info("=" * 60)
    kunfu_panda_logger.info("🎯 STARTING PAY CALCULATOR DATA PROCESS")
    kunfu_panda_logger.info("=" * 60)
    
    try:
        kunfu_panda_logger.info("📡 Step 1: Fetching pay calculator data from API...")
        calculator_records = fetch_pay_calculator_data_from_api()
        
        if not calculator_records:
            kunfu_panda_logger.info("📭 No data to process")
            return 0
        
        kunfu_panda_logger.info(f"✅ Step 1 Complete: Fetched {len(calculator_records)} records")
        
        kunfu_panda_logger.info("💾 Step 2: Storing records in database...")
        stored_count = 0
        skipped_count = 0
        failed_count = 0
        
        chunk_size = 100
        total_chunks = (len(calculator_records) + chunk_size - 1) // chunk_size
        
        for i in range(0, len(calculator_records), chunk_size):
            chunk = calculator_records[i:i + chunk_size]
            chunk_number = i // chunk_size + 1
            
            kunfu_panda_logger.info(f"  💾 Processing Chunk {chunk_number}/{total_chunks} ({len(chunk)} records)")
            
            for record_data in chunk:
                try:
                    calculator, created = store_pay_calculator_data(record_data)
                    if created:
                        stored_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    failed_count += 1
                    record_id = record_data.get("_id", "unknown")
                    kunfu_panda_logger.error(f"  ❌ Error processing record {record_id}: {str(e)}")
                    continue
            
            kunfu_panda_logger.info(
                f"  ✅ Chunk {chunk_number} Complete: {stored_count} stored, "
                f"{skipped_count} skipped, {failed_count} failed so far"
            )
        
        kunfu_panda_logger.info("=" * 60)
        kunfu_panda_logger.info("🎉 PAY CALCULATOR DATA PROCESS COMPLETED!")
        kunfu_panda_logger.info(f"📊 FINAL RESULTS:")
        kunfu_panda_logger.info(f"  ✅ Successfully Stored: {stored_count} records")
        kunfu_panda_logger.info(f"  ⏭️  Skipped (already exist): {skipped_count} records")
        kunfu_panda_logger.info(f"  ❌ Failed: {failed_count} records")
        if (stored_count + skipped_count + failed_count) > 0:
            success_rate = (stored_count / (stored_count + skipped_count + failed_count) * 100)
            kunfu_panda_logger.info(f"  📈 Success Rate: {success_rate:.1f}%")
        kunfu_panda_logger.info("=" * 60)
        
        return stored_count
        
    except Exception as e:
        kunfu_panda_logger.error(f"Fatal error in pay calculator data process: {str(e)}")
        raise

