from django.db import models


from django.db import models

from preference.models import Age, Country, FactoryFarm, Gender, Language, Organisation, OrganisationSector, Route, SectorOfWork

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
    event_created_at = models.DateTimeField(null=True, blank=True)
    event_updated_at = models.DateTimeField(null=True, blank=True)
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
    
    
class ChaptersFeedbackStandard(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    api_created_at = models.DateTimeField(null=True, blank=True)
    api_updated_at = models.DateTimeField(null=True, blank=True)
    data_source_id = models.CharField(max_length=255, null=True, blank=True)
    device_id = models.CharField(max_length=255,null=True, blank=True)
    locale = models.CharField(max_length=255, null=True, blank=True)
    preference = models.ForeignKey('preference.Preference', on_delete=models.CASCADE, null=True, blank=True, related_name='chapter_feedback_preference')
    feedback_title = models.CharField(null=True, blank=True, max_length=255)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    age = models.ForeignKey(Age, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    origin = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='chapter_feedback_origin')
    destination = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='chapter_feedback_destination')
    destination_state = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='chapter_feedback_destination_state')
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    organisation_sector = models.ForeignKey(OrganisationSector, on_delete=models.SET_NULL, null=True, blank=True)
    factory_farm = models.ForeignKey(FactoryFarm, on_delete=models.SET_NULL, null=True, blank=True)
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True, blank=True)
    sectors_of_work = models.ManyToManyField(SectorOfWork)

    
class ChaptersFeedback(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    feedback_standard = models.ForeignKey(ChaptersFeedbackStandard, on_delete=models.CASCADE, null=True)
    question = models.CharField(null=True, blank=True, max_length=255)
    response = models.CharField(null=True, blank=True, max_length=255)