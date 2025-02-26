from django.core.management.base import BaseCommand
from preference.logic.add_orgcode_to_preferences import add_organisation_data_to_db


class Command(BaseCommand):
    help = "Add organization data to the database"

    def handle(self, *args, **options):
        try:
            created_count, updated_count = add_organisation_data_to_db()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully processed organizations. Created: {created_count}, Updated: {updated_count}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing organizations: {str(e)}"))
