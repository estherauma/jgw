import glob
import os

from dashboard.models import JGWCache
from django.core.management.base import BaseCommand
from jgwpandas.settings import CACHE_DIR


class Command(BaseCommand):
    help = "Clears current cache, both file and database."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--category", type=str, help="Data category whose cache you want to remove.")

    def handle(self, *args, **options):
        category = options.get("--category")
        if category:
            result = JGWCache.objects.filter(category=category)
            result.delete()
            for f in glob.glob(os.path.join(CACHE_DIR, f"{category}*.csv")):
                os.remove(f)
        JGWCache.objects.all().delete()
        for f in glob.glob(os.path.join(CACHE_DIR, "*.csv")):
            os.remove(f)
