from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Create a superuser if none exists'

    def handle(self, *args, **options):
        if not User.objects.filter(email='superuser@fiftyeight.io').exists():
            User.objects.create_superuser(email='superuser@fiftyeight.io', password='superuser@123')
            self.stdout.write(self.style.SUCCESS('Superuser created.'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists.'))
