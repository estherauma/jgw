from common.app_events import AppEvents
from common.const.value_const import BIGQUERY_HOMEPAGE_EVENTS_START_DATE
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

        event_instances = []

        for event in homepage_events:
            event_date = event.get('event_date')
            device_id = event.get('deviceId')
            app_id = event.get('appId')
            locale = event.get('locale')
            organisation_code = event.get('organisation_code')

            language = Language.objects.filter(code=event.get('language')).first()
            age = Age.objects.filter(range=event.get('age')).first()
            gender = Gender.objects.filter(name=event.get('gender')).first()

            organisation_name = event.get('organisation')
            organisation = None
            if organisation_name:
                organisation = Organisation.objects.filter(name=organisation_name.lower()).first()

            destination_name=event.get('destination')
            destination=None
            if destination_name:
                destination = Country.objects.filter(code=destination_name.lower()).first()

            if destination and destination.name.lower() == 'malaysia' and organisation is None:
                organisation = Organisation.objects.filter(name="not specified").first()

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

        BigqueryHomepageEventData.objects.bulk_create(event_instances)

        print(f"{len(homepage_events)} homepage events saved to the database.")

    except Exception as e:
        print(f"An error occurred while saving homepage events: {str(e)}")