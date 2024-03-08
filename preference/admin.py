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


@admin.register(SectorOfWork)
class SectorOfWorkTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["name", "translated_name", "translated_to"]
    search_fields = ["translated_name", "name"]


@admin.register(Gender)
class GenderTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["name", "translated_name", "translated_to"]
    search_fields = ["translated_name", "name"]


@admin.register(Language)
class LanguageTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["code", "name", "translated_name", "translated_to"]
    search_fields = ["translated_name", "name", "code"]


@admin.register(Preference)
class PreferenceTabularAdminDisplay(admin.ModelAdmin):
    list_display = [
        "id",
        "get_translated_name",
        "get_origin_name",
        "destination",
        "age_translated_name",
        "is_missing_sector_cleaned",
    ]
    search_fields = ["gender__translated_name", "origin__name", "destination__name"]

    def get_translated_name(self, obj):
        return obj.gender.translated_name if obj.gender else None

    def age_translated_name(self, obj):
        return obj.age.translated_range if obj.age else None

    def get_origin_name(self, obj):
        return obj.origin.name if obj.origin else None


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


# Register your models here.
@admin.register(OrganisationSector)
class OrganisationSectorAdmin(admin.ModelAdmin):
    pass


@admin.register(FactoryFarm)
class FactoryFarmAdmin(admin.ModelAdmin):
    pass


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    pass


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    pass


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(Age)
class AgeAdmin(admin.ModelAdmin):
    pass
