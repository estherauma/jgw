from dashboard.tasks import fetch_API_data
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Pulls, cleans and caches all or selected data categories from the JGW API."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--category", type=str, help="Data category whose cache you want to seed.")

    def handle(self, *args, **options):
        category = options.get("--category")
        if category:
            self.stdout.write(self.style.HTTP_INFO(f"Seeding cache for category: {category}."))
            fetch_API_data.delay(category=category)
        fetch_API_data.delay()
