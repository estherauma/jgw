from django.core.management.base import BaseCommand
from common.helpers.preference_helpers.events import chapter_tittle_match_to_chapter_ids

from events.logic.process_chapters import update_chapter_table_with_chapter_tittle

class Command(BaseCommand):
    def handle(self, *args, **options):
       update_chapter_table_with_chapter_tittle(chapter_tittle_match_to_chapter_ids)

