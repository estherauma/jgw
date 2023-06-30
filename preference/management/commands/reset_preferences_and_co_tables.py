from django.core.management.base import BaseCommand

from preference.models import FactoryFarm, Organisation, OrganisationSector, Preference, SectorOfWork



class Command(BaseCommand):
    def handle(self, *args, **options):
        FactoryFarm.objects.all().delete()
        Organisation.objects.all().delete()
        OrganisationSector.objects.all().delete()
        Preference.objects.all().delete()
        SectorOfWork.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully reset preferences and co tables'))
