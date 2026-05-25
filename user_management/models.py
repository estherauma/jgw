from django.conf import settings
from django.db import models
from django.utils import timezone
import secrets
import string
from waffle.models import Flag

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


class ShortLink(models.Model):
    code = models.CharField(max_length=16, unique=True)
    target_url = models.URLField(max_length=2048)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.expires_at is not None and self.expires_at <= timezone.now()

    @classmethod
    def create_url_short_link(cls, target_url, expires_at=None, length=8, max_attempts=5):
        alphabet = string.ascii_letters + string.digits
        for _ in range(max_attempts):
            code = ''.join(secrets.choice(alphabet) for _ in range(length))
            if not cls.objects.filter(code=code).exists():
                return cls.objects.create(
                    code=code,
                    target_url=target_url,
                    expires_at=expires_at,
                )
        raise ValueError("Unable to generate unique short link code.")


class UserVerificationCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_codes",
    )
    purpose = models.CharField(max_length=64, db_index=True)
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "purpose", "created_at"]),
        ]

    def is_expired(self):
        return self.expires_at <= timezone.now()
