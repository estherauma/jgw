from django.core.management.base import BaseCommand

from events.logic.process_chapters import update_chapter_table_with_chapter_tittle

class Command(BaseCommand):
    def handle(self, *args, **options):
        update_chapter_table_with_chapter_tittle()

