from django.core.management.base import BaseCommand
from content.models import Collection, Locale, WorkSector

class Command(BaseCommand):
    help = "Instantly inserts mock local data for Task 3"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database options...")

        locales = [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
        ]
        for item in locales:
            Locale.objects.get_or_create(code=item["code"], defaults={"name": item["name"]})

        sectors = [
            {"slug": "agriculture", "display_name": "Agriculture"},
            {"slug": "hospitality", "display_name": "Hospitality"},
            {"slug": "manufacturing", "display_name": "Manufacturing"},
        ]
        for item in sectors:
            WorkSector.objects.get_or_create(slug=item["slug"], defaults={"display_name": item["display_name"]})

        collections = [
            {"name": "Default Collection", "api_name": "default_collection"},
            {"name": "Partner Options", "api_name": "partner_options"},
        ]
        for item in collections:
            Collection.objects.get_or_create(api_name=item["api_name"], defaults={"name": item["name"]})

        self.stdout.write(self.style.SUCCESS("Successfully seeded test configurations!"))