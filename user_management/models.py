from django.db import models
from django.conf import settings

from preference.models import (
    Language,
    OrganisationAccessCode,
    OrganisationData,
)

class AuditFieldsMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name="%(app_label)s_%(class)s_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="%(app_label)s_%(class)s_updated"
    )
    
    class Meta:
        abstract = True
class WorkGroup(models.Model):
    name = models.CharField(max_length=255)
    organisation = models.ForeignKey(
        OrganisationData, on_delete=models.CASCADE, related_name="work_groups"
    )
    access_codes = models.ManyToManyField(
        OrganisationAccessCode, blank=True, related_name="work_groups"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organisation", "name"], name="unique_workgroup_name_per_org"
            )
        ]


class AppUser(models.Model):
    password = models.CharField(blank=True, max_length=128)
    first_name = models.CharField(blank=True, null=False, max_length=128)
    last_name = models.CharField(blank=True, null=False, max_length=128)
    email = models.EmailField(null=False, blank=False, max_length=128, unique=True)
    phone_number = models.CharField(blank=True, null=True, max_length=32)
    phone_country_iso = models.CharField(blank=True, null=True, max_length=2)
    organisation_data = models.ForeignKey(
        OrganisationData, on_delete=models.PROTECT, null=True, blank=True
    )
    work_groups = models.ManyToManyField(WorkGroup, blank=True, related_name="users")
    user_languages = models.ManyToManyField(Language, blank=True)

    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Designates whether this user should be treated as active.\nUnselect this instead of deleting accounts.",
    )
    receive_marketing_emails = models.BooleanField(
        default=False, help_text="Designates whether this user should receive marketing emails."
    )
    class Meta:
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.email}"
