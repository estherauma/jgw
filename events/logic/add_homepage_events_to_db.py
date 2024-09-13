from common.app_events import AppEvents
from common.const.value_const import BIGQUERY_HOMEPAGE_EVENTS_START_DATE
from common.helpers.model_helpers.common import bulk_create_in_chunks
from common.utils.date_utils import todays_date
from events.models import BigqueryHomepageEventData
from preference.models import Country, Language, Age, Gender, Organisation


def fetch_homepage_events_from_bigquery():
    start_date = BIGQUERY_HOMEPAGE_EVENTS_START_DATE
    end_date = todays_date()

    latest_homepage_event = BigqueryHomepageEventData.objects.last()
    if latest_homepage_event:
        start_date = latest_homepage_event.event_date.strftime("%Y-%m-%d")

    appEvents = AppEvents()
    latest_homepage_events_result = appEvents.bigquery_homepage_data(
        start_date=start_date, end_date=end_date
    )

    return latest_homepage_events_result

def fetch_and_save_homepage_events_to_db():
    try:
        homepage_events = fetch_homepage_events_from_bigquery()

        languages = {lang.code: lang for lang in Language.objects.all()}
        ages = {age.range: age for age in Age.objects.all()}
        genders = {gender.name: gender for gender in Gender.objects.all()}
        organisations = {org.name.lower(): org for org in Organisation.objects.all()}
        countries = {country.code.lower(): country for country in Country.objects.all()}

        organisation_not_specified = organisations.get("not specified")

        event_instances = []

        for event in homepage_events:
            event_date = event.get('event_date')
            device_id = event.get('deviceId')
            app_id = event.get('appId')
            locale = event.get('locale')
            organisation_code = event.get('organisation_code')

            language = languages.get(event.get('language'))
            age = ages.get(event.get('age'))
            gender = genders.get(event.get('gender'))
            organisation_name = event.get('organisation')
            organisation = organisations.get(organisation_name.lower()) if organisation_name else None

            destination_name = event.get('destination')
            destination = countries.get(destination_name.lower()) if destination_name else None

            if destination and destination.name.lower() == 'malaysia' and organisation is None:
                organisation = organisation_not_specified

            event_instance = BigqueryHomepageEventData(
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
            )
            event_instances.append(event_instance)

        bulk_create_in_chunks(BigqueryHomepageEventData, event_instances)

        print(f"{len(homepage_events)} homepage events saved to the database.")

    except Exception as e:
        print(f"An error occurred while saving homepage events: {str(e)}")
