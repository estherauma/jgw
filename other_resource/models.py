from django.db import models

from preference.models import Organisation

# Create your models here.
class OtherResource(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField()
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title