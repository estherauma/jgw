from django.core.management.base import BaseCommand, CommandParser

from events.logic.add_chapters_feedback_data import fetch_chapters_feedback_from_api_to_db
from events.logic.add_chapters_opened_data import fetch_chapters_opened_data_from_api_to_db
from events.logic.add_sws_pasi_data import fetch_sws_pasi_events_from_api_to_db
from events.logic.add_links_click_data import fetch_links_click_events_from_api_to_db


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("data_types", nargs="*", type=str, help="Add chapters feedback")

    def handle(self, *args, **options):
        events_data_functions = {
            "chapters_opened": fetch_chapters_opened_data_from_api_to_db,
            "chapters_feedback": fetch_chapters_feedback_from_api_to_db,
            "sws_pasi_events": fetch_sws_pasi_events_from_api_to_db,
            "links_click_events": fetch_links_click_events_from_api_to_db,
        }
        data_types = options["data_types"]

        if not data_types:
            print("No data type provided")
            return

        if "all" in data_types:
            for func in events_data_functions.values():
                func()
            return

        for data_type in data_types:
            if data_type in events_data_functions:
                events_data_functions[data_type]()
            else:
                print(f"Unknown data type: {data_type}")
