from django.core.management.base import BaseCommand
from preference.logic.add_pay_calculator_data import fetch_and_store_pay_calculator_data
from common.logger import KunfuPandaLogger

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/pay_calculator_command.log")


class Command(BaseCommand):
    help = "Fetches and stores pay calculator data from the JGW API"

    def handle(self, *args, **options):
        kunfu_panda_logger.info("Starting pay calculator data fetch and store process")

        try:
            stored_count = fetch_and_store_pay_calculator_data()

            success_message = (
                f"Pay calculator data fetch and store completed:\n"
                f"- Stored {stored_count} new records\n"
            )

            self.stdout.write(self.style.SUCCESS(success_message))
            kunfu_panda_logger.info(success_message)

        except Exception as e:
            error_message = f"Error in pay calculator data fetch and store process: {str(e)}"
            self.stdout.write(self.style.ERROR(error_message))
            kunfu_panda_logger.error(error_message)
            raise

