from django.core.management.base import BaseCommand
from preference.models import PayCalculator
from common.logger import KunfuPandaLogger

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/pay_calculator_command.log")


class Command(BaseCommand):
    help = "Resets the PayCalculator table by deleting all records"

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        count = PayCalculator.objects.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING('PayCalculator table is already empty'))
            kunfu_panda_logger.info("PayCalculator table reset attempted but table is already empty")
            return
        
        if not options['confirm']:
            confirm = input(
                f'Are you sure you want to delete all {count} PayCalculator records? (yes/no): '
            )
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Operation cancelled'))
                kunfu_panda_logger.info("PayCalculator table reset cancelled by user")
                return
        
        try:
            deleted_count = PayCalculator.objects.all().delete()[0]
            success_message = f'Successfully deleted {deleted_count} PayCalculator record(s)'
            self.stdout.write(self.style.SUCCESS(success_message))
            kunfu_panda_logger.info(success_message)
        except Exception as e:
            error_message = f'Error resetting PayCalculator table: {str(e)}'
            self.stdout.write(self.style.ERROR(error_message))
            kunfu_panda_logger.error(error_message)
            raise

