from django.db import models

from preference.models import Preference

# Create your models here.
class HelpContact(models.Model):
    data_source_id = models.CharField(max_length=100)
    deviceI_id = models.CharField(max_length=100)
    app_id = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    cleaned = models.BooleanField(default=False)

    def __str__(self):
        return f"phone: {self.phone_number} ------- email: {self.email}"