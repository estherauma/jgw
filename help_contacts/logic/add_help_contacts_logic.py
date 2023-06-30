from django.db import transaction
from common.const.value_const import NOT_SPECIFIED

from common.services.api_client import JustGoodWorkAPIClient
from help_contacts.models import HelpContact
from preference.models import Preference


def fetch_help_contacts_from_api(client):
    return client.get_data("/help-contacts")

@transaction.atomic
def fetch_help_contacts_from_api_to_db():
    
    jgw_api_client = JustGoodWorkAPIClient()
    help_contacts = fetch_help_contacts_from_api(jgw_api_client)
    
    for help_contact in help_contacts:
        try:
            add_help_contacts_to_db(help_contact)
        except Exception as e:
            print('An error occurred during preference creation:', str(e))
            transaction.set_rollback(True)
            raise
 
       
def add_help_contacts_to_db(help_contact):
    # get preference from db by device_id
    preference = Preference.objects.get(device_id=help_contact.get('deviceId'))
    
    # use the preference id when creating the help_contact
    HelpContact.objects.create(
        data_source_id= help_contact.get('_id'),
        deviceI_id= help_contact.get('deviceId'),
        app_id= help_contact.get('appId'),
        phone_number= help_contact.get('phoneNumber') or NOT_SPECIFIED,
        email= help_contact.get('email') or NOT_SPECIFIED,
        createdAt= help_contact.get('createdAt'),
        updatedAt= help_contact.get('updatedAt'),
        preference= preference
    )  