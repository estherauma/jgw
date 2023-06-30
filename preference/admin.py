from django.contrib import admin

from preference.models import (
        FactoryFarm, 
        Organisation, 
        OrganisationSector, 
        Preference, 
        SectorOfWork
    )


# Register your models here.
admin.site.register(SectorOfWork)
admin.site.register(OrganisationSector)
admin.site.register(FactoryFarm)
admin.site.register(Organisation)
admin.site.register(Preference)