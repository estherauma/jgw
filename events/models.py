from django.db import models


from django.db import models

from preference.models import Age, Country, Gender, Language, Organisation, OrganisationSector

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BigQueryChaptersData(TimestampedModel):
    event_date = models.DateField()
    chapters = models.CharField(max_length=50)
    users = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.chapters

class BigQueryFirstOpenHomepageData(TimestampedModel):
    """
        This model is used to store data from BigQueryFirstOpenHomepageData
        event_name are :  homepage, first_open
    """
    event_date = models.DateField()
    users = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    event_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.event_name
    

class OneTimeEventJob(TimestampedModel):
    name = models.CharField(max_length=255)
    run = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    
    
class ChaptersOpened(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_name = models.CharField(max_length=255)
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, blank=True)
    age = models.ForeignKey(Age, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    organisation_sector = models.ForeignKey(OrganisationSector, on_delete=models.SET_NULL, null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    app_id = models.CharField(max_length=255, null=True, blank=True)
    locale = models.CharField(max_length=255, null=True, blank=True)
    destination_state = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='chapters_opened_destination_state')
    destination = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='chapters_opened_destination')
    
    def __str__(self):
        return f"ChaptersOpened {self.event_name}"