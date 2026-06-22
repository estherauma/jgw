from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from preference.forms import SectorsOfWorkMapperForm
from preference.resources import PreferenceResource, PreferenceHistoryResource

from preference.models import (
    FactoryFarm,
    ImmigrationStatus,
    Organisation,
    OrganisationAccessCode,
    OrganizationGroup,
    OrganisationData,
    OrganisationDeepLink,
    OrganisationSector,
    OriginalSectorOfWork,
    PayCalculator,
    Preference,
    SectorOfWork,
    SiteLanguages,
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
    PreferenceHistory,
    DashboardPreferences,
    ChartSettings,
)


@admin.register(SectorOfWork)
class SectorOfWorkTabularAdminDisplay(admin.ModelAdmin):
    list_display = [
        "created_at",
        "name",
        "translated_name",
        "translated_to",
        "original_sector_of_work",
        "is_original_sector_of_work_in_english",
        "is_disabled",
    ]
    search_fields = ["translated_name", "name", "is_disabled", "is_original_sector_of_work_in_english"]


@admin.register(Gender)
class GenderTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["name", "translated_name", "translated_to"]
    search_fields = ["translated_name", "name"]


@admin.register(Language)
class LanguageTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["code", "name", "translated_name", "translated_to"]
    search_fields = ["translated_name", "name", "code"]


@admin.register(Preference)
class PreferenceTabularAdminDisplay(ExportActionModelAdmin, admin.ModelAdmin):
    resource_class = PreferenceResource
    list_display = [
        "id",
        "data_source_id",
        "device_id",
        "created_at",
        "api_created_at",
        "get_translated_name",
        "get_origin_name",
        "destination",
        "org_code",
        "organisation",
        "org_info",
        "get_age_translated_name",
        "is_missing_sector_cleaned",
        "get_org_workcode",
        "immigration_status",
        "is_missing_accesscode_cleaned",
        "is_myvoice_organisation",
        "is_missing_organisation_info_cleaned",
    ]
    search_fields = [
        "id",
        "created_at",
        "data_source_id",
        "device_id",
        "gender__translated_name",
        "origin__name",
        "destination__name",
        "is_missing_sector_cleaned",
        "is_missing_accesscode_cleaned",
        "immigration_status",
    ]
    ordering = ["-api_created_at"]
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


@admin.register(OriginalSectorOfWork)
class OriginalSectorOfWorkAdmin(admin.ModelAdmin):
    list_display = ["language", "key", "value", "display_name"]
    search_fields = ["language", "key", "value", "display_name"]


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
    list_display = ["code", "organisation", "created_at", "updated_at"]


@admin.register(ImmigrationStatus)
class ImmigrationStatusAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "created_at", "updated_at"]


@admin.register(OrganisationData)
class OrganisationDataAdmin(admin.ModelAdmin):
    readonly_fields = [
        "cms_id",
        "org_code"
    ]
    search_fields = [
        "name",
        "org_code",
        "display_name",
        "organization_group__name",
        "organization_group__group_code",
        "custom_type",
        "theme",
        "default_report_issue_emails",
        "default_feedback_emails",
        "work_sector",
        "content_collection",
        "default_collection_language",
        "cms_id",
        "big_icon_cms_media_id",
        "small_icon_cms_media_id",
        "cms_sync_status",
    ]
    list_display = [
        "name",
        "org_code",
        "display_name",
        "organization_group",
        "has_custom_content",
        "custom_type",
        "theme",
        "work_sector",
        "content_collection",
        "default_collection_language",
        "cms_id",
        "big_icon_cms_media_id",
        "small_icon_cms_media_id",
        "cms_sync_status",
        "last_cms_sync_date",
        "created_at",
        "updated_at",
    ]


@admin.register(OrganisationDeepLink)
class OrganisationDeepLinkAdmin(admin.ModelAdmin):
    search_fields = ["title", "link", "link_type", "organisation_data__name", "organisation_data__org_code"]
    list_display = ["title", "link_type", "link", "organisation_data", "created_at", "updated_at"]
    list_select_related = ["organisation_data"]


@admin.register(OrganizationGroup)
class OrganizationGroupAdmin(admin.ModelAdmin):
    search_fields = ["name", "group_code"]
    list_display = ["name", "group_code", "created_at", "updated_at"]


@admin.register(SiteLanguages)
class SiteLanguagesAdmin(admin.ModelAdmin):
    search_fields = ["organisation__name", "code", "name"]
    list_display = ["organisation", "code", "name", "created_at", "updated_at"]


@admin.register(PreferenceHistory)
class PreferenceHistoryAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    resource_class = PreferenceHistoryResource
    list_display = [
        "id",
        "data_source_id",
        "device_id",
        "created_at",
        "api_created_at",
        "get_translated_name",
        "get_origin_name",
        "destination",
        "org_code",
        "organisation",
        "org_info",
        "get_age_translated_name",
        "get_org_workcode",
        "immigration_status",
        "is_missing_organisation_info_cleaned",
    ]
    search_fields = [
        "id",
        "created_at",
        "data_source_id",
        "device_id",
        "gender__translated_name",
        "origin__name",
        "destination__name",
    ]

    def get_translated_name(self, obj):
        return obj.gender.translated_name if obj.gender else None

    def get_age_translated_name(self, obj):
        return obj.age.translated_range if obj.age else None

    def get_origin_name(self, obj):
        return obj.origin.name if obj.origin else None

    def get_org_workcode(self, obj):
        return obj.organisation_access_code.code if obj.organisation_access_code else None

@admin.register(DashboardPreferences)
class DashboardPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'version', 'filter_start_date', 'filter_end_date', 'updated_at', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['user', 'created_at', 'updated_at']
    list_filter = ['version', 'created_at', 'updated_at', 'filter_start_date', 'filter_end_date']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'version')
        }),
        ('Date Filters', {
            'fields': ('filter_start_date', 'filter_end_date')
        }),
        ('Preferences', {
            'fields': ('layout', 'chart_definitions'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = []


@admin.register(ChartSettings)
class ChartSettingsAdmin(admin.ModelAdmin):
    list_display = ['dashboard_preferences', 'chart_id', 'chart_type', 'size', 'enabled', 'start_date', 'end_date', 'updated_at']
    search_fields = ['chart_id', 'dashboard_preferences__user__email']
    list_filter = ['chart_id', 'chart_type', 'enabled', 'size', 'start_date', 'end_date', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Chart Information', {
            'fields': ('dashboard_preferences', 'chart_id', 'chart_type', 'size', 'enabled')
        }),
        ('Date Filters', {
            'fields': ('start_date', 'end_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PayCalculator)
class PayCalculatorAdmin(admin.ModelAdmin):
    list_display = [
        "device_id",
        "preference",
        "organisation",
        "organisation_access_code",
        "origin",
        "destination",
        "age",
        "gender",
        "total_left",
        "total_estimated_pay",
        "api_created_at",
        "created_at",
    ]
    search_fields = [
        "device_id",
        "organisation__name",
        "destination__name",
        "age__range",
        "gender__name",
    ]
    list_filter = [
        "destination",
        "organisation",
        "age",
        "gender",
        "immigration_status",
        "api_created_at",
    ]
    readonly_fields = [
        "device_id",
        "api_created_at",
        "api_updated_at",
        "created_at",
        "updated_at",
    ]
    date_hierarchy = "api_created_at"
    raw_id_fields = ["preference"]
