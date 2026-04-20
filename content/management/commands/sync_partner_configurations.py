from django.core.management.base import BaseCommand

from content.services.partner_configurations import sync_partner_configurations


class Command(BaseCommand):
    help = "Sync organisation partner configurations from the CMS."

    def handle(self, *args, **options):
        self.stdout.write("Syncing organisation partner configurations from CMS...")
        summary = sync_partner_configurations()

        if summary is None:
            self.stderr.write(
                self.style.ERROR("Failed to sync organisation partner configurations.")
            )
            return

        self.stdout.write(self.style.SUCCESS("Successfully synced organisation partner configurations."))
        self.stdout.write(self.style.SUCCESS(f"Sync summary: {summary}"))

