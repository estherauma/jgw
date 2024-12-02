from django.core.management.base import BaseCommand
from preference.logic.update_preference_immigration_status import update_preferences_immigration_status


class Command(BaseCommand):
    help = "Updates immigration status for preferences from JGW API"

    def handle(self, *args, **options):
        try:
            updated_count = update_preferences_immigration_status()
            self.stdout.write(
                self.style.SUCCESS(f"Successfully updated immigration status for {updated_count} preferences")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error updating immigration status: {str(e)}"))
