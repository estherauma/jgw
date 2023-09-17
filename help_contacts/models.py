from django.db import models

from preference.models import Route

# Create your models here.
class HelpContact(models.Model):
    data_source_id = models.CharField(max_length=100)
    device_id = models.CharField(max_length=100)
    app_id = models.CharField(max_length=100)
    locale = models.CharField(max_length=255, null=True, blank=False)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    cleaned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone_number} : {self.email}"