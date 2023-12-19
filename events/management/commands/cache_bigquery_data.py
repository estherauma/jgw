from django.core.management.base import BaseCommand, CommandParser

from events.logic.add_chapters_feedback_data import fetch_chapters_feedback_from_api_to_db
from events.logic.add_chapters_opened_data import fetch_chapters_opened_data_from_api_to_db
from events.logic.add_sws_pasi_data import fetch_sws_pasi_events_from_api_to_db
from events.logic.add_links_click_data import fetch_links_click_events_from_api_to_db


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("data_type", type=str, help="Add chapters feedback")

    def handle(self, *args, **options):
        if options["data_type"] == "chapter_feedback":
            fetch_chapters_feedback_from_api_to_db()
        else:
            fetch_chapters_opened_data_from_api_to_db()
            fetch_chapters_feedback_from_api_to_db()
            fetch_sws_pasi_events_from_api_to_db()
            fetch_links_click_events_from_api_to_db()
