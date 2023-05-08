

from common.help_contacts import HelpContacts
from dashboard.models import TranslatedText


def load_phone_number():
        preferences = HelpContacts()
        unique_phone_number_list = preferences.unique_help_contacts_list("phoneNumber")

        # get the existing values from the database
        existing_values = set(TranslatedText.objects.values_list('original_text', flat=True))

        new_phone_numbers = []
        for phone_number in unique_phone_number_list:
            if phone_number not in existing_values:
                new_phone_numbers.append(TranslatedText(original_text=phone_number))
        # bulk create only the new values
        TranslatedText.objects.bulk_create(new_phone_numbers)