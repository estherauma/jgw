from django.db import models

# Create your models here.
from django.db import models

class SectorOfWork(models.Model):
    name = models.CharField(max_length=255)
    translated_name = models.CharField(max_length=255, null=True, blank=True)
    translated_to = models.CharField(max_length=255, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

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

class CountryState(models.Model):
    name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name}'
    
class LocationOfPotentialWork(models.Model):
    name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name}'

class Country(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    code = models.CharField(max_length=50, null=True, blank=True, unique=True)
    api_value = models.CharField(max_length=255, null=True, blank=False)
    is_origin = models.BooleanField(default=False)
    is_destination = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name}'

class Language(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, null=True, blank=True)
    translated_name = models.CharField(max_length=255, null=True, blank=True)
    translated_to = models.CharField(max_length=255, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name}"
    
class Route(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.name
    

class Gender(models.Model):
    name = models.CharField(max_length=255)
    translated_name = models.CharField(max_length=255, null=True, blank=True)
    translated_to = models.CharField(max_length=255, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.translated_name}"
    
class Age(models.Model):
    range = models.CharField(max_length=255)
    translated_range = models.CharField(max_length=255, null=True, blank=True)
    translated_to = models.CharField(max_length=255, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.range


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
    
    location_of_potential_work = models.ForeignKey(LocationOfPotentialWork, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    age = models.ForeignKey(Age, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    origin = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='origin')
    destination = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='destination')
    destination_state = models.ForeignKey(CountryState, on_delete=models.SET_NULL, null=True, blank=True, related_name='destination_state')
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    
    sectors_of_work = models.ManyToManyField(SectorOfWork)
    organisation_sector = models.ForeignKey(OrganisationSector, on_delete=models.SET_NULL, null=True, blank=True)
    factory_farm = models.ForeignKey(FactoryFarm, on_delete=models.SET_NULL, null=True, blank=True)
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Preference {self.id}"
        