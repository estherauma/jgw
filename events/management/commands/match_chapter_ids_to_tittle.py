from django.core.management.base import BaseCommand
from events.logic.chapter_title_api_data import update_chapter_titles, update_chapters_by_immigration_status


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_chapter_titles()
        update_chapters_by_immigration_status()
