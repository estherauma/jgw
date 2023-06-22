from django.db import models

# Create your models here.
from django.db import models

class SectorOfWork(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class OrganisationSector(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name   
    
class FactoryFarm(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Organisation(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Preference(models.Model):
    data_source_id = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    updated_at = models.DateTimeField()
    location_of_potential_work = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    age = models.CharField(max_length=255)
    route = models.CharField(max_length=255)
    locale = models.CharField(max_length=255)
    app_id = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    language = models.CharField(max_length=255)
    origin = models.CharField(max_length=255, null=True)
    destination = models.CharField(max_length=255, null=True)
    cleaned = models.BooleanField(default=False)
    
    sectors_of_work = models.ManyToManyField(SectorOfWork)
    organisation_sector = models.ForeignKey(OrganisationSector, on_delete=models.CASCADE)
    factory_farm = models.ForeignKey(FactoryFarm, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)

    def __str__(self):
        return f"Preference {self.id}"

