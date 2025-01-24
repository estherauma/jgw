from django.core.management.base import BaseCommand
from django.db import transaction
from preference.models import Preference
from common.logger import KunfuPandaLogger


class Command(BaseCommand):
    help = 'Reverse the org_info updates by setting org_info to null and is_missing_organisation_info_cleaned to False'

    def handle(self, *args, **kwargs):
        kunfu_panda_logger = KunfuPandaLogger()
        
        try:
            with transaction.atomic():
                preferences_to_reverse = Preference.objects.filter(
                    is_missing_organisation_info_cleaned=True
                )
                
                count = preferences_to_reverse.count()
                
                preferences_to_reverse.update(
                    org_info=None,
                    is_missing_organisation_info_cleaned=False
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully reversed org_info updates for {count} preferences'
                    )
                )
                kunfu_panda_logger.info(f"Reversed org_info updates for {count} preferences")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reversing preferences org_info updates: {str(e)}')
            )
            kunfu_panda_logger.error(f"Error reversing org_info updates: {str(e)}") 