from django.db import models


from django.db import models

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BigQueryChaptersData(TimestampedModel):
    event_date = models.DateField()
    chapters = models.CharField(max_length=50)
    users = models.IntegerField()
    count = models.IntegerField()
    
    def __str__(self):
        return self.chapters

class BigQueryFirstOpenHomepageData(TimestampedModel):
    """
        This model is used to store data from BigQueryFirstOpenHomepageData
        event_name are :  homepage, first_open
    """
    event_date = models.DateField()
    users = models.IntegerField()
    count = models.IntegerField()
    event_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.event_name
    

class OneTimeEventJob(TimestampedModel):
    name = models.CharField(max_length=255)
    run = models.BooleanField(default=False)

    def __str__(self):
        return self.name