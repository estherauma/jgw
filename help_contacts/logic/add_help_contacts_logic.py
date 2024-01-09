from django.db import transaction
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, NOT_SPECIFIED
from common.helpers.model_helpers.preference import get_or_add_country_to_db, get_or_add_route_to_db
from common.helpers.preference_helpers.country import (
    get_data_destination,
    get_data_origin,
)
from common.logger import KunfuPandaLogger

from common.services.api_client import JustGoodWorkAPIClient
from common.utils.date_utils import todays_date
from help_contacts.models import HelpContact
from help_contacts.task import translate_and_clean_help_contact_fields
from preference.models import Preference


def fetch_help_contacts_from_api(client):
    return client.get_data("/help-contacts")


kunfu_panda_logger = KunfuPandaLogger(log_file="logs/help_contacts_tasks.log")


def fetch_help_contacts_from_api(client):
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    # get the last time inline question were fetched
    latest_help_contact = HelpContact.objects.last()
    if latest_help_contact:
        start_date = latest_help_contact.created_at.strftime("%Y-%m-%d")

    kunfu_panda_logger.info(f"Fetching help contacts from {start_date} to {end_date}")

    return client.get_data(f"/help-contacts?startDate={start_date}&endDate={end_date}")


@transaction.atomic
def fetch_help_contacts_from_api_to_db():
    jgw_api_client = JustGoodWorkAPIClient()
    help_contacts = fetch_help_contacts_from_api(jgw_api_client)

    for help_contact in help_contacts:
        try:
            add_help_contacts_to_db(help_contact)
        except Exception as e:
            transaction.set_rollback(True)
            raise
    kunfu_panda_logger.info(f"Added {len(help_contacts)} help contacts to the database")
    translate_and_clean_help_contact_fields()


def get_contact_value_and_type(help_contact_dict):
    email = help_contact_dict.get("email")
    phone_number = help_contact_dict.get("phoneNumber")

    if email:
        return {"contact_value": email, "contact_type": "email"}

    if phone_number:
        return {"contact_value": phone_number, "contact_type": "phone"}

    return {"contact_value": NOT_SPECIFIED, "contact_type": NOT_SPECIFIED}


def add_help_contacts_to_db(help_contact):
    # get preference from db by device_id
    device_id = help_contact.get("deviceId")
    route = help_contact.get("route")
    data_source_id = help_contact.get("_id")

    if HelpContact.objects.filter(data_source_id=data_source_id).exists():
        return

    preference = Preference.objects.filter(device_id=device_id).first()

    route_data = get_or_add_route_to_db(route)

    location_of_potential_work = help_contact.get("location_of_potential_work")
    origin = get_data_origin(route=route, api_origin=help_contact.get("locale"))
    destination = get_data_destination(
        route=route,
        api_destination=help_contact.get("destination"),
        location_of_potential_work=location_of_potential_work,
    )

    origin_data = get_or_add_country_to_db(origin, source="origin")
    destination_data = get_or_add_country_to_db(destination, source="destination")

    # use the preference id when creating the help_contact
    HelpContact.objects.create(
        contact_type=get_contact_value_and_type(help_contact).get("contact_type"),
        contact_value=get_contact_value_and_type(help_contact).get("contact_value"),
        data_source_id=data_source_id,
        device_id=device_id,
        app_id=help_contact.get("appId"),
        locale=help_contact.get("locale"),
        route=route_data,
        origin=origin_data,
        destination=destination_data,
        api_created_at=help_contact.get("createdAt"),
        api_updated_at=help_contact.get("updatedAt"),
        preference=preference,
    )
