from django.db import models

class InlineQuestion(models.Model):
    data_source_id = models.CharField(max_length=24)
    device_id = models.CharField(max_length=255)
    app_id = models.CharField(max_length=255)
    locale = models.CharField(max_length=255)
    route = models.CharField(max_length=255)
    language = models.CharField(max_length=255)
    organisation = models.CharField(max_length=255, blank=True)
    organisation_sector = models.CharField(max_length=255, blank=True)
    factory_farm = models.CharField(max_length=255, blank=True)
    recruiter_kept_id = models.CharField(max_length=255)
    are_you_sure = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    
    def __str__(self):
        return f"InlineQuestion {self.id}"
