from django.core.management.base import BaseCommand
from content.models import Collection, Locale, WorkSector

class Command(BaseCommand):
    help = "Instantly inserts mock local data for Task 3"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database options...")

        locales = [
            {"code": "en-us", "name": "English - United States"},
            {"code": "fr-mg", "name": "French - Madagascar"},
            {"code": "ar-sy", "name": "Arabic - Syria"},
            {"code": "en-ug", "name": "English - Uganda"},
            {"code": "es-es", "name": "Spanish - Spain"},
        ]
        for item in locales:
            Locale.objects.get_or_create(code=item["code"], defaults={"name": item["name"]})

        sectors = [
            {"slug": "agriculture", "display_name": "Agriculture"},
            {"slug": "hospitality", "display_name": "Hospitality"},
            {"slug": "transport", "display_name": "Transport"},
            {"slug": "cleaning", "display_name": "Cleaning"},
            {"slug": "construction", "display_name": "Construction"},
        ]
        for item in sectors:
            WorkSector.objects.get_or_create(slug=item["slug"], defaults={"display_name": item["display_name"]})

        collections = [
            {"name": "Seasonal Worker Scheme", "api_name": "seasonal-worker-scheme"},
            {"name": "Okolabor", "api_name": "okolabor"},
            {"name": "JGW USA", "api_name": "jgw-usa"},
            {"name": "JGW UK", "api_name": "jgw-uk"},
            {"name": "JGW Spain", "api_name": "jgw-spain"},
        ]
        for item in collections:
            Collection.objects.get_or_create(api_name=item["api_name"], defaults={"name": item["name"]})

        self.stdout.write(self.style.SUCCESS("Successfully seeded test configurations!"))