from django.db import models

# Create your models here.
from django.db import models

from common.const.value_const import NOT_SPECIFIED


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


class OrganisationAccessCode(models.Model):
    code = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


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
    is_missing_accesscode_cleaned = models.BooleanField(default=False)


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
