from django.db import models
from django.utils import timezone
from django.conf import settings
from common.models import AuditFieldsMixin

from common.const.value_const import (
    CMS_SYNC_FAILED,
    CMS_SYNC_PENDING,
    CMS_SYNC_SUCCESS,
    NOT_SPECIFIED,
    ORGANISATION_THEME_CHOICES,
)

CMS_SYNC_STATUS_CHOICES = [
        (CMS_SYNC_PENDING, "Pending"),
        (CMS_SYNC_SUCCESS, "Success"),
        (CMS_SYNC_FAILED, "Failed"),
    ]
class OriginalSectorOfWork(models.Model):
    language = models.CharField(max_length=10)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.display_name} ({self.language})"


class SectorOfWork(models.Model):
    name = models.CharField(max_length=255)
    translated_name = models.CharField(max_length=255, null=True, blank=True)
    translated_to = models.CharField(max_length=255, default="en")
    is_disabled = models.BooleanField(default=False)
    is_original_sector_of_work_in_english = models.BooleanField(default=False)
    original_sector_of_work = models.ForeignKey(
        OriginalSectorOfWork,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sectors_of_work_english",
    )
    translated_to = models.CharField(max_length=255, default="en")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.translated_name


class OrganisationSector(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FactoryFarm(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]


class Organisation(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class LocationOfPotentialWork(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, null=True, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Country(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    code = models.CharField(max_length=50, null=True, blank=True, unique=True)
    api_value = models.CharField(max_length=255, null=True, blank=False)
    is_origin = models.BooleanField(default=False)
    is_destination = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]


class CountryState(models.Model):
    name = models.CharField(max_length=255, default=NOT_SPECIFIED)
    country = models.ForeignKey(
        Country, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="country_states"
    )
    full_name = models.CharField(max_length=255, null=True, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Language(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, null=True, blank=True)
    translated_name = models.CharField(max_length=255, null=True, blank=True)
    translated_to = models.CharField(max_length=255, default="en")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.translated_name}"


class Route(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Gender(models.Model):
    name = models.CharField(max_length=255)
    translated_name = models.CharField(max_length=255, null=True, blank=True)
    translated_to = models.CharField(max_length=255, default="en")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Age(models.Model):
    range = models.CharField(max_length=255)
    translated_range = models.CharField(max_length=255, null=True, blank=True)
    translated_to = models.CharField(max_length=255, default="en")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.range


class OrganisationAccessCode(AuditFieldsMixin):
    code = models.CharField(max_length=255, unique=True)
    requires_login = models.BooleanField(default=False)
    organisation = models.ForeignKey(
        "OrganisationData",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organisation_access_codes",
    )
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.code
    
class ImmigrationStatus(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

class OrganizationGroup(AuditFieldsMixin):
    name = models.CharField(max_length=255, unique=True)
    group_code = models.CharField(max_length=50, unique=True)
    cms_id = models.CharField(max_length=255, null=True, blank=True)
    last_cms_sync_date = models.DateTimeField(null=True, blank=True)
    cms_sync_status = models.CharField(
        max_length=20,
        choices=CMS_SYNC_STATUS_CHOICES,
        default=CMS_SYNC_PENDING,
    )
    custom_type = models.CharField(max_length=100, default="organization_group")


    def __str__(self):
        return self.name


class OrganisationData(AuditFieldsMixin):
    

    name = models.CharField(max_length=255)
    org_code = models.CharField(max_length=50, unique=True)
    organization_group = models.ForeignKey(
        OrganizationGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organizations",
    )
    display_name = models.CharField(max_length=255, null=True, blank=True)
    has_custom_content = models.BooleanField(default=True)
    theme = models.CharField(max_length=100, choices=ORGANISATION_THEME_CHOICES, null=True, blank=True)
    default_report_issue_emails = models.TextField(null=True, blank=True)
    default_feedback_emails = models.TextField(null=True, blank=True)
    big_icon = models.TextField(null=True, blank=True)
    big_icon_cms_media_id = models.BigIntegerField(null=True, blank=True)
    small_icon = models.TextField(null=True, blank=True)
    small_icon_cms_media_id = models.BigIntegerField(null=True, blank=True)
    cms_id = models.CharField(max_length=255, null=True, blank=True)
    custom_type = models.CharField(max_length=100, default="version_1")
    work_sector = models.CharField(max_length=255, null=True, blank=True)
    content_collection = models.CharField(max_length=255, null=True, blank=True)
    default_collection_language = models.CharField(max_length=100, null=True, blank=True)
    last_cms_sync_date = models.DateTimeField(null=True, blank=True)
    cms_sync_status = models.CharField(
        max_length=20,
        choices=CMS_SYNC_STATUS_CHOICES,
        default=CMS_SYNC_PENDING,
    )

    def __str__(self):
        return self.name
    class Meta(AuditFieldsMixin.Meta):
        indexes = [
            models.Index(fields=['name']),
        ]


class SiteLanguages(AuditFieldsMixin):
    organisation = models.ForeignKey(
        "OrganisationData",
        on_delete=models.CASCADE,
        related_name="collection_languages",
    )
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        if self.name:
            return f"{self.code} ({self.name})"
        return self.code

    class Meta(AuditFieldsMixin.Meta):
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['organisation']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['organisation', 'code'],
                name='unique_site_language_per_organisation',
            )
        ]


class Preference(models.Model):
    data_source_id = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    locale = models.CharField(max_length=255, null=True, blank=True)
    app_id = models.CharField(max_length=255, null=True, blank=True)
    cleaned = models.BooleanField(default=False)

    api_created_at = models.DateTimeField()
    api_updated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    location_of_potential_work = models.ForeignKey(
        LocationOfPotentialWork, on_delete=models.SET_NULL, null=True, blank=True
    )
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    age = models.ForeignKey(Age, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    origin = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="origin"
    )
    destination = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="destination"
    )
    api_destination = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="api_destination"
    )
    destination_state = models.ForeignKey(
        CountryState, on_delete=models.SET_NULL, null=True, blank=True, related_name="destination_state"
    )
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    sectors_of_work = models.ManyToManyField(SectorOfWork, related_name="pref_sectors_of_work")
    organisation_sector = models.ForeignKey(
        OrganisationSector, on_delete=models.SET_NULL, null=True, blank=True
    )
    immigration_status = models.ForeignKey(
        ImmigrationStatus, on_delete=models.SET_NULL, null=True, blank=True
    )
    org_code = models.CharField(max_length=255, null=True, blank=True)
    org_info = models.ForeignKey(
        OrganisationData,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pref_org_info",
    )
    organisation_access_code = models.ForeignKey(
        OrganisationAccessCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pref_org_access_code",
    )
    factory_farm = models.ForeignKey(FactoryFarm, on_delete=models.SET_NULL, null=True, blank=True)
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, blank=True)
    is_missing_sector_cleaned = models.BooleanField(default=False)
    is_myvoice_organisation = models.BooleanField(default=False)
    is_missing_accesscode_cleaned = models.BooleanField(default=False)
    is_missing_organisation_info_cleaned = models.BooleanField(default=False)

    class Meta:
        indexes = [
            # Date-based filtering
            models.Index(fields=['api_created_at']),
            
            # Foreign key fields used in filtering
            models.Index(fields=['org_info']),
            models.Index(fields=['factory_farm']),
            models.Index(fields=['destination']),
            models.Index(fields=['origin']),
            models.Index(fields=['language']),
            models.Index(fields=['immigration_status']),
            
            # Composite indexes for common query patterns
            models.Index(fields=['api_created_at', 'org_info']),
            models.Index(fields=['api_created_at', 'destination']),
            models.Index(fields=['api_created_at', 'origin']),
        ]


class TextTranslations(models.Model):
    original_text = models.TextField()
    translated_text = models.TextField(null=True, blank=True)


class SwsCountry(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.country.name


class SectorsOfWorkMapper(models.Model):
    mapper = models.CharField(max_length=255)
    sectors = models.ManyToManyField(SectorOfWork)

    def __str__(self):
        return self.mapper


class DashboardPreferences(models.Model):
    """User dashboard customization preferences"""
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='dashboard_prefs',
        primary_key=True
    )
    layout = models.JSONField(default=dict, blank=True, help_text="Dashboard layout configuration")
    chart_definitions = models.JSONField(default=dict, blank=True, help_text="Chart definitions metadata")
    version = models.IntegerField(default=1, help_text="Version of dashboard preferences schema")

    filter_start_date = models.DateField(null=True, blank=True, help_text="Default start date for dashboard filters")
    filter_end_date = models.DateField(null=True, blank=True, help_text="Default end date for dashboard filters")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dashboard Preferences"
        verbose_name_plural = "Dashboard Preferences"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['filter_start_date', 'filter_end_date']),
        ]

    def __str__(self):
        return f"Dashboard Preferences for {self.user.email}"

    def get_layout(self):
        """Get layout or return empty dict"""
        return self.layout if self.layout else {'rows': []}

    def get_chart_settings_dict(self):
        """Get all chart settings as a dictionary (for backward compatibility)"""
        settings_dict = {}
        for chart_setting in self.chart_settings.all():
            settings_dict[chart_setting.chart_id] = {
                'chart_type': chart_setting.chart_type,
                'size': chart_setting.size,
                'enabled': bool(chart_setting.enabled), 
                'start_date': chart_setting.start_date.isoformat() if chart_setting.start_date else None,
                'end_date': chart_setting.end_date.isoformat() if chart_setting.end_date else None,
            }
        return settings_dict


class ChartSettings(models.Model):
    """Individual chart settings for dashboard preferences"""
    CHART_TYPE_CHOICES = [
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('doughnut', 'Doughnut Chart'),
        ('area', 'Area Chart'),
        ('map', 'Map'),
    ]
    
    dashboard_preferences = models.ForeignKey(
        DashboardPreferences,
        on_delete=models.CASCADE,
        related_name='chart_settings'
    )
    chart_id = models.CharField(max_length=100, db_index=True, help_text="Chart identifier from CHART_DEFINITIONS")
    chart_type = models.CharField(
        max_length=20,
        choices=CHART_TYPE_CHOICES,
        default='bar',
        help_text="Type of chart to display"
    )
    size = models.IntegerField(default=6, help_text="Column size (1-12 for Bootstrap grid)")
    enabled = models.BooleanField(default=True, help_text="Whether this chart is enabled")
    
    start_date = models.DateField(null=True, blank=True, help_text="Start date filter for this chart")
    end_date = models.DateField(null=True, blank=True, help_text="End date filter for this chart")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chart Setting"
        verbose_name_plural = "Chart Settings"
        unique_together = [['dashboard_preferences', 'chart_id']]
        indexes = [
            models.Index(fields=['dashboard_preferences', 'chart_id']),
            models.Index(fields=['chart_id']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.chart_id} settings for {self.dashboard_preferences.user.email}"

    def to_dict(self):
        """Convert to dictionary format"""
        return {
            'chart_type': self.chart_type,
            'size': self.size,
            'enabled': self.enabled,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
        }


class PreferenceHistory(models.Model):
    data_source_id = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    locale = models.CharField(max_length=255, null=True, blank=True)
    app_id = models.CharField(max_length=255, null=True, blank=True)
    cleaned = models.BooleanField(default=False)

    api_created_at = models.DateTimeField()
    api_updated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    location_of_potential_work = models.ForeignKey(
        LocationOfPotentialWork, on_delete=models.SET_NULL, null=True, blank=True
    )
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    age = models.ForeignKey(Age, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    origin = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="pref_history_origin"
    )
    destination = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="pref_history_destination"
    )
    api_destination = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="pref_history_api_destination"
    )
    destination_state = models.ForeignKey(
        CountryState, on_delete=models.SET_NULL, null=True, blank=True, related_name="pref_history_destination_state"
    )
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name="pref_history_route")
    sectors_of_work = models.ManyToManyField(SectorOfWork, related_name="pref_history_sectors_of_work")
    organisation_sector = models.ForeignKey(
        OrganisationSector, on_delete=models.SET_NULL, null=True, blank=True, related_name="pref_history_organisation_sector"
    )
    immigration_status = models.ForeignKey(
        ImmigrationStatus, on_delete=models.SET_NULL, null=True, blank=True
    )
    org_code = models.CharField(max_length=255, null=True, blank=True)
    org_info = models.ForeignKey(
        OrganisationData,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pref_history_org_info",
    )
    organisation_access_code = models.ForeignKey(
        OrganisationAccessCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pref_history_org_access_code",
    )
    factory_farm = models.ForeignKey(FactoryFarm, on_delete=models.SET_NULL, null=True, blank=True)
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, blank=True)
    is_missing_organisation_info_cleaned = models.BooleanField(default=False)


class PayCalculator(models.Model):
    device_id = models.CharField(max_length=255, db_index=True)
    preference = models.ForeignKey(Preference, on_delete=models.SET_NULL, null=True, blank=True)
    age = models.ForeignKey(Age, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    immigration_status = models.ForeignKey(ImmigrationStatus, on_delete=models.SET_NULL, null=True, blank=True)
    destination = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="pay_calculator_destination")
    origin = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="pay_calculator_origin")
    destination_state = models.ForeignKey(CountryState, on_delete=models.SET_NULL, null=True, blank=True)
    organisation = models.ForeignKey(OrganisationData, on_delete=models.SET_NULL, null=True, blank=True)
    organisation_access_code = models.ForeignKey(OrganisationAccessCode, on_delete=models.SET_NULL, null=True, blank=True)
    factory_farm = models.ForeignKey(FactoryFarm, on_delete=models.SET_NULL, null=True, blank=True)
    sectors_of_work = models.ManyToManyField(SectorOfWork, related_name="pay_calculator_sectors_of_work")
    sectors = models.ManyToManyField(OriginalSectorOfWork, related_name="pay_calculator_sectors")
    
    total_left = models.FloatField(null=True, blank=True)
    tax_reclaim = models.FloatField(null=True, blank=True)

    total_estimated_pay = models.FloatField(null=True, blank=True)
    weeks_worked = models.IntegerField(null=True, blank=True)
    income_tax = models.FloatField(null=True, blank=True)
    national_insurance = models.FloatField(null=True, blank=True)
    average_week_hours = models.IntegerField(null=True, blank=True)

    total_estimated_cost = models.FloatField(null=True, blank=True)
    accomadation_per_week = models.FloatField(null=True, blank=True)
    transportation_within_uk = models.FloatField(null=True, blank=True)
    visa_appointment_one_off = models.FloatField(null=True, blank=True)
    travel_home_to_uk_one_off = models.FloatField(null=True, blank=True)
    food_per_week = models.FloatField(null=True, blank=True)

    api_created_at = models.DateTimeField()
    api_updated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['device_id']),
            models.Index(fields=['api_created_at']),
            models.Index(fields=['destination']),
        ]
        ordering = ['-api_created_at']
    
    def __str__(self):
        return f"PayCalculator - {self.device_id} - {self.api_created_at}"
