from django.core.management.base import BaseCommand
from django.utils import timezone
from question.logic.add_message_data_sent import fetch_and_store_message_data
from common.logger import KunfuPandaLogger

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/message_data_command.log")


class Command(BaseCommand):
    help = "Fetches and stores message data from the JGW API"

    def handle(self, *args, **options):
        kunfu_panda_logger.info("Starting message data fetch and store process")

        try:
            stored_count = fetch_and_store_message_data()

            success_message = (
                f"Message data fetch and store completed:\n" f"- Stored {stored_count} new messages\n"
            )

            self.stdout.write(self.style.SUCCESS(success_message))
            kunfu_panda_logger.info(success_message)

        except Exception as e:
            error_message = f"Error in message data fetch and store process: {str(e)}"
            self.stdout.write(self.style.ERROR(error_message))
            kunfu_panda_logger.error(error_message)
            raise
