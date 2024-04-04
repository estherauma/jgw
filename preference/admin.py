from django.contrib import admin
from preference.forms import SectorsOfWorkMapperForm

from preference.models import (
    FactoryFarm,
    Organisation,
    OrganisationAccessCode,
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
    list_display = ["created_at", "name", "translated_name", "translated_to", "is_disabled"]
    search_fields = ["translated_name", "name", "is_disabled"]


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
        "created_at",
        "get_translated_name",
        "get_origin_name",
        "destination",
        "get_age_translated_name",
        "is_missing_sector_cleaned",
        "get_org_workcode",
        "is_missing_accesscode_cleaned",
    ]
    search_fields = [
        "created_at",
        "gender__translated_name",
        "origin__name",
        "destination__name",
        "is_missing_sector_cleaned",
        "is_missing_accesscode_cleaned",
    ]

    def get_translated_name(self, obj):
        return obj.gender.translated_name if obj.gender else None

    def get_age_translated_name(self, obj):
        return obj.age.translated_range if obj.age else None

    def get_origin_name(self, obj):
        return obj.origin.name if obj.origin else None

    def get_org_workcode(self, obj):
        return obj.organisation_access_code.code if obj.organisation_access_code else None


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
    search_fields = ["name"]
    list_display = ["name", "created_at", "updated_at"]


@admin.register(FactoryFarm)
class FactoryFarmAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "created_at", "updated_at"]


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "created_at", "updated_at"]


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "created_at", "updated_at"]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ["name", "is_origin", "code", "api_value"]
    list_display = ["name", "code", "api_value", "is_origin", "is_destination", "created_at", "updated_at"]


@admin.register(Age)
class AgeAdmin(admin.ModelAdmin):
    search_fields = ["range", "translated_range", "translated_to"]
    list_display = ["range", "translated_range", "translated_to", "created_at", "updated_at"]


@admin.register(OrganisationAccessCode)
class OrganisationAccessCodeAdmin(admin.ModelAdmin):
    search_fields = ["code"]
    list_display = ["code", "created_at", "updated_at"]
