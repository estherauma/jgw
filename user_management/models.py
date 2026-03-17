from django.db import models
from django.conf import settings

from preference.models import (
    OrganisationAccessCode,
    OrganisationData,
)
from common.models import AuditFieldsMixin
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
        constraints = [
            models.UniqueConstraint(
                fields=["organisation", "name"], name="unique_workgroup_name_per_org"
            )
        ]

