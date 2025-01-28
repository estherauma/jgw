from django.core.management.base import BaseCommand
from django.db import transaction
from question.models import MessageDataSent
from common.logger import KunfuPandaLogger

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/message_data.log")


class Command(BaseCommand):
    help = "Resets the MessageDataSent table by deleting all records"

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            count = MessageDataSent.objects.count()

            MessageDataSent.objects.all().delete()

            success_message = f"Successfully deleted {count} records from MessageDataSent table."
            self.stdout.write(self.style.SUCCESS(success_message))
            kunfu_panda_logger.info(success_message)

        except Exception as e:
            error_message = f"Error resetting MessageDataSent table: {str(e)}"
            self.stdout.write(self.style.ERROR(error_message))
            kunfu_panda_logger.error(error_message)
            raise
