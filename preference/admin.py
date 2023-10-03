from django.contrib import admin

from preference.models import (
        FactoryFarm, 
        Organisation, 
        OrganisationSector, 
        Preference, 
        SectorOfWork, 
        Route,
        Language,
        Gender,
        Country,
        Age,
        LocationOfPotentialWork,
        CountryState,
    )

class SectorOfWorkTabularAdminDisplay(admin.ModelAdmin):
    list_display = ['name', 'translated_name', 'translated_to']
    search_fields = ['translated_name', 'name']
 
class GenderTabularAdminDisplay(admin.ModelAdmin):
    list_display = ['name', 'translated_name', 'translated_to']
    search_fields = ['translated_name', 'name']   


class LanguageTabularAdminDisplay(admin.ModelAdmin):
    list_display = ['code', 'name', 'translated_name', 'translated_to']
    search_fields = ['translated_name', 'name', 'code']  
    
# Register your models here.
admin.site.register(SectorOfWork, SectorOfWorkTabularAdminDisplay)
admin.site.register(OrganisationSector)
admin.site.register(FactoryFarm)
admin.site.register(Organisation)
admin.site.register(Preference)
admin.site.register(Route)
admin.site.register(Language, LanguageTabularAdminDisplay)
admin.site.register(Gender, GenderTabularAdminDisplay)
admin.site.register(Country)
admin.site.register(Age)
admin.site.register(LocationOfPotentialWork)
admin.site.register(CountryState)