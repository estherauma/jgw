
from django.core.management.base import BaseCommand

from common.help_contacts import HelpContacts
from dashboard.models import TranslatedText


def add_new_contacts():
    help_contacts = HelpContacts()
    unique_phone_number_list = help_contacts.unique_help_contacts_list("phoneNumber")

    # get the existing values from the database
    existing_values = set(TranslatedText.objects.values_list('original_text', flat=True))

    new_phone_numbers = []
    for phone_number in unique_phone_number_list:
        if phone_number not in existing_values:
            new_phone_numbers.append(TranslatedText(original_text=phone_number))
    # bulk create only the new values
    TranslatedText.objects.bulk_create(new_phone_numbers)


    
class Command(BaseCommand):
    def handle(self, *args, **options):
        add_new_contacts()
