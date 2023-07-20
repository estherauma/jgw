from django.core.management.base import BaseCommand

from preference.models import (
        FactoryFarm, 
        Organisation, 
        OrganisationSector, 
        Preference, 
        SectorOfWork, 
        Route,
        Language,
        Gender,
        Country
    )


class Command(BaseCommand):
    def handle(self, *args, **options):
        FactoryFarm.objects.all().delete()
        Organisation.objects.all().delete()
        OrganisationSector.objects.all().delete()
        SectorOfWork.objects.all().delete()
        Route.objects.all().delete()
        Language.objects.all().delete()
        Gender.objects.all().delete()
        Country.objects.all().delete()
        Preference.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully reset preferences and co tables'))
