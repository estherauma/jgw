from django.conf import settings
from django.db import models
from waffle.models import Flag

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


class OrganisationRole(models.Model):
    organisation = models.ForeignKey(
        OrganisationData, on_delete=models.CASCADE, related_name="roles"
    )
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    grants_dashboard_access = models.BooleanField(
        default=False,
        help_text="When enabled, users in this role should access the dashboard.",
    )
    is_system = models.BooleanField(
        default=False,
        help_text="Marks default roles created by the system; not a user-created role.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.organisation})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organisation", "name"],
                name="unique_role_name_per_org",
            )
        ]


class OrganisationRolePermission(models.Model):
    role = models.ForeignKey(
        OrganisationRole, on_delete=models.CASCADE, related_name="role_permissions"
    )
    flag = models.ForeignKey(
        Flag, on_delete=models.CASCADE, related_name="role_permissions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["role", "flag"],
                name="unique_role_flag_permission",
            )
        ]


class OrganisationRoleAssignment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="org_roles"
    )
    organisation = models.ForeignKey(
        OrganisationData, on_delete=models.CASCADE, related_name="role_assignments"
    )
    role = models.ForeignKey(
        OrganisationRole, on_delete=models.CASCADE, related_name="assignments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organisation"],
                name="unique_role_assignment_per_org",
            )
        ]
