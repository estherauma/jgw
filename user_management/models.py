from django.db import models
from django.conf import settings

from preference.models import (
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
class WorkGroup(AuditFieldsMixin):
    name = models.CharField(max_length=255)
    organisation = models.ForeignKey(
        OrganisationData, on_delete=models.CASCADE, related_name="work_groups"
    )
    access_codes = models.ManyToManyField(
        OrganisationAccessCode, blank=True, related_name="work_groups"
    )

    def __str__(self):
        return self.name
    class Meta(AuditFieldsMixin.Meta):
        abstract = False
        constraints = [
            models.UniqueConstraint(
                fields=["organisation", "name"], name="unique_workgroup_name_per_org"
            )
        ]

