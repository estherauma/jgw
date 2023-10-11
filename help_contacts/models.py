from django.db import models
from common.const.value_const import NOT_SPECIFIED

from preference.models import Country, Route

class HelpContact(models.Model):
    CONTACT_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone Number'),
        ('web', 'Web Address'),
        (NOT_SPECIFIED, NOT_SPECIFIED)
    ]

    contact_type = models.CharField(
        max_length=255,
        choices=CONTACT_CHOICES,
        null=True,
        blank=False
    )
    
    data_source_id = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    app_id = models.CharField(max_length=255)
    locale = models.CharField(max_length=255, null=True, blank=False)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name="help_contact_route")
    contact_value = models.CharField(max_length=255, blank=False, null=True)
    translated_contact_value = models.CharField(max_length=255, blank=True, null=True)
    api_created_at = models.DateTimeField()
    api_updated_at = models.DateTimeField()
    cleaned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    origin = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='help_contact_origin')
    destination = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='help_contact_destination')
    preference = models.ForeignKey('preference.Preference', on_delete=models.CASCADE, null=True, blank=True, related_name='help_contact_preference')