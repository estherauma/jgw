from django.db import models

from preference.models import Organisation
from django.contrib.auth.models import Group

# Create your models here.
class OtherResource(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField()
    group=models.ForeignKey(Group,on_delete=models.CASCADE,null=True,blank=True)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title