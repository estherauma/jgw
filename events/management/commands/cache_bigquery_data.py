from django.core.management.base import BaseCommand

from events.logic.add_chapters_feedback_data import fetch_chapters_feedback_from_api_to_db
from events.logic.add_chapters_opened_data import fetch_chapters_opened_data_from_api_to_db

    
class Command(BaseCommand):
    def handle(self, *args, **options):
        
        fetch_chapters_opened_data_from_api_to_db()
        fetch_chapters_feedback_from_api_to_db()
