
from django.core.management.base import BaseCommand

from common.preferences import Preferences
from dashboard.models import TranslatedText


class Command(BaseCommand):
    def handle(self, *args, **options):
        preferences = Preferences()
        unique_gender_list = preferences.unique_series_list("gender")
        print(unique_gender_list)

        # get the existing values from the database
        existing_values = set(TranslatedText.objects.values_list('original_text', flat=True))

        new_genders = []
        for gender in unique_gender_list:
            if gender not in existing_values:
                new_genders.append(TranslatedText(original_text=gender))

        # bulk create only the new values
        TranslatedText.objects.bulk_create(new_genders)
