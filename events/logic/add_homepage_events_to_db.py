from django.db import transaction
from common.app_events import AppEvents
from datetime import datetime
from common.const.value_const import BIGQUERY_HOMEPAGE_EVENTS_START_DATE
from common.helpers.model_helpers.common import bulk_create_in_chunks
from common.helpers.model_helpers.preference import get_or_add_country_to_db, get_or_add_immigration_status_to_db
from common.logger import KunfuPandaLogger
from events.models import BigqueryHomepageEventData
from preference.logic.update_perference_organisation_info import update_bigquery_homepage_event_org_info_from_organisation
from preference.models import Country, Language, Age, Gender, Organisation

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/homepage_events.log")

def get_latest_homepage_event_timestamp():
    latest_event = BigqueryHomepageEventData.objects.order_by('-event_date').first()
    if latest_event:
        return datetime.combine(latest_event.event_date, datetime.min.time())
    return datetime.strptime(BIGQUERY_HOMEPAGE_EVENTS_START_DATE, "%Y-%m-%d")


def fetch_homepage_events_from_bigquery_in_batches(batch_size=5000, last_event_timestamp=None):
    try:
        appEvents = AppEvents()
        homepage_events = appEvents.bigquery_homepage_data(
            batch_size=batch_size,
            last_event_timestamp=last_event_timestamp
        )
        return homepage_events
    except Exception as e:
        kunfu_panda_logger.error(f"Error fetching data from BigQuery: {str(e)}")
        raise

def fetch_and_save_homepage_events_to_db():
    try:
        last_event_timestamp = get_latest_homepage_event_timestamp()
    except Exception as e:
        kunfu_panda_logger.error(f"Error getting the last event timestamp in the database: {str(e)}")
        raise

    batch_size = 5000
    total_fetched = 0

    languages = {lang.code: lang for lang in Language.objects.all()}
    ages = {age.range: age for age in Age.objects.all()}
    genders = {gender.name: gender for gender in Gender.objects.all()}
    organisations = {org.name.lower(): org for org in Organisation.objects.all()}
    countries = {country.code.lower(): country for country in Country.objects.all()}
    organisation_not_specified = organisations.get("not specified")

    while True:
        try:
            homepage_events = fetch_homepage_events_from_bigquery_in_batches(
                batch_size=batch_size,
                last_event_timestamp=last_event_timestamp
            ) or []

            if not homepage_events:
                break

            event_instances = []
            for event in homepage_events:
                try:
                    event_instance = create_homepage_event_instance(
                        event,
                        languages,
                        ages,
                        genders,
                        organisations,
                        countries,
                        organisation_not_specified
                    )
                    event_instances.append(event_instance)
                except Exception as e:
                    kunfu_panda_logger.error(f"Error processing homepage event: {str(e)}")
                    continue

            if event_instances:
                bulk_create_in_chunks(BigqueryHomepageEventData, event_instances, chunk_size=100)

            last_event_timestamp = homepage_events[-1]["event_timestamp"]
            total_fetched += len(homepage_events)

            kunfu_panda_logger.info(
                f"Processed {len(homepage_events)} homepage events in current batch. Total processed: {total_fetched}"
            )

            event_instances.clear()

        except Exception as e:
            kunfu_panda_logger.error(f"Error processing batch: {str(e)}")
            raise

    kunfu_panda_logger.info(f"Finished adding {total_fetched} homepage events to the database")

    update_myvoice_bigquery_homepage_events()
    update_bigquery_homepage_event_org_info_from_organisation()

def create_homepage_event_instance(event, languages, ages, genders, organisations, countries, organisation_not_specified):
    event_date = event.get("event_date")
    device_id = event.get("deviceId")
    app_id = event.get("appId")
    locale = event.get("locale")
    organisation_code = event.get("organisationCode")

    language = languages.get(event.get("language"))
    age = ages.get(event.get("age"))
    gender = genders.get(event.get("gender"))
    immigrationStatus = event.get("immigrationStatus")
    geo_city = event.get("geoCity")
    geo_country = event.get("geoCountry")
    
    organisation_name = event.get("organisation")
    organisation = organisations.get(organisation_name.lower()) if organisation_name else organisation_not_specified

    destination_name = event.get("destination")
    destination = countries.get(destination_name.lower()) if destination_name else None

    geo_country = get_or_add_country_to_db(geo_country)
    immigration_status = get_or_add_immigration_status_to_db(immigrationStatus)

    return BigqueryHomepageEventData(
        event_date=event_date,
        device_id=device_id,
        app_id=app_id,
        language=language,
        locale=locale,
        destination=destination,
        age=age,
        gender=gender,
        organisation=organisation,
        organisation_code=organisation_code,
        immigration_status=immigration_status,
        geo_city=geo_city,
        geo_country=geo_country
    )

def update_myvoice_bigquery_homepage_events():
    with transaction.atomic():
        not_specified_org = Organisation.objects.get(name="not specified")
        myvoice_org = Organisation.objects.get(name="myvoice")
        malaysia_country = Country.objects.get(name="malaysia")
        myvoice_access_code = "myv2112"

        bigquery_homepage_events_to_update = BigqueryHomepageEventData.objects.filter(
            organisation=not_specified_org, destination=malaysia_country
        )

        updated_count = bigquery_homepage_events_to_update.update(
            organisation=myvoice_org, organisation_code=myvoice_access_code, is_myvoice_organisation=True
        )

    return updated_count


def reverse_myvoice_bigquery_homepage_events():
    with transaction.atomic():

        not_specified_org = Organisation.objects.get(name="not specified")

        preferences_to_reverse = BigqueryHomepageEventData.objects.filter(is_myvoice_organisation=True)

        updated_count = preferences_to_reverse.update(
            organisation=not_specified_org, organisation_code=None, is_myvoice_organisation=False
        )

    return updated_count
