from django.db import models

from preference.models import (
    OrganisationAccessCode,
    OrganisationData,
)


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

