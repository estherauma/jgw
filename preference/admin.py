from django.contrib import admin
from preference.forms import SectorsOfWorkMapperForm

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
    SectorsOfWorkMapper,
    TextTranslations,
    LocationOfPotentialWork,
    CountryState,
    SwsCountry,
)


class SectorOfWorkTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["name", "translated_name", "translated_to"]
    search_fields = ["translated_name", "name"]


class GenderTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["name", "translated_name", "translated_to"]
    search_fields = ["translated_name", "name"]


class LanguageTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["code", "name", "translated_name", "translated_to"]
    search_fields = ["translated_name", "name", "code"]


class PreferenceTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["id", "gender", "origin", "destination", "age", "is_missing_sector_cleaned"]


# Register your models here.
admin.site.register(SectorOfWork, SectorOfWorkTabularAdminDisplay)
admin.site.register(OrganisationSector)
admin.site.register(FactoryFarm)
admin.site.register(Organisation)
admin.site.register(Preference, PreferenceTabularAdminDisplay)
admin.site.register(Route)
admin.site.register(Language, LanguageTabularAdminDisplay)
admin.site.register(Gender, GenderTabularAdminDisplay)
admin.site.register(Country)
admin.site.register(Age)


@admin.register(TextTranslations)
class TextTranslationsTable(admin.ModelAdmin):
    list_display = ["original_text", "translated_text"]
    search_fields = ["original_text", "translated_text"]


admin.site.register(LocationOfPotentialWork)


@admin.register(CountryState)
class CountryStateList(admin.ModelAdmin):
    list_display = ["name", "full_name", "country"]
    search_fields = ["name", "full_name"]


@admin.register(SwsCountry)
class SwsCountryAdmin(admin.ModelAdmin):
    list_display = ["country"]


@admin.register(SectorsOfWorkMapper)
class SectorsOfWorkMapperAdmin(admin.ModelAdmin):
    form = SectorsOfWorkMapperForm
    list_display = ["mapper"]
