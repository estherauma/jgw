from django.core.management.base import BaseCommand

from events.logic.process_chapters import update_chapter_table_with_chapter_tittle,fetch_chapters_data_from_JGW_api

class Command(BaseCommand):
    def handle(self, *args, **options):
       fetch_chapters_data_from_JGW_api()

