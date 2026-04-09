from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.conf import settings
from common.models import AuditFieldsMixin
from django.db import models
from preference.models import Country, FactoryFarm, ImmigrationStatus, Language, Organisation, OrganisationData
from decimal import Decimal

ROLES = ["SCHEME", "FACTORY", "STAFF", "ADMIN"]
USER_TYPE_CHOICES = [
    ("dashboard", "Dashboard"),
    ("app", "Mobile App"),
]
STATUS = ["PENDING", "ACCEPTED", "SENT"]


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set!")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, AuditFieldsMixin):
    objects = UserManager()
    USERNAME_FIELD = "email"
    ROLE = models.TextChoices("Role", " ".join(ROLES))
    password = models.CharField(blank=True, max_length=128)
    first_name = models.CharField(blank=True, null=False, max_length=128)
    last_name = models.CharField(blank=True, null=False, max_length=128)
    role = models.CharField(blank=True, null=True, choices=ROLE.choices, max_length=16)
    access_type = models.CharField(
        blank=False,
        null=False,
        choices=USER_TYPE_CHOICES,
        max_length=16,
        default="dashboard",
    )
    scheme = models.ForeignKey(
        to="dashboard.Scheme", on_delete=models.DO_NOTHING, null=True, max_length=16, blank=True
    )
    email = models.EmailField(null=True, blank=True, max_length=128, unique=True)
    phone_number = models.CharField(blank=True, null=True, max_length=32)
    phone_country_iso = models.CharField(blank=True, null=True, max_length=2)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    factories = models.ManyToManyField(FactoryFarm, blank=True)
    organisations = models.ManyToManyField(Organisation, blank=True)
    organisation_data = models.ManyToManyField(OrganisationData, blank=True)
    work_groups = models.ManyToManyField("user_management.WorkGroup", blank=True, related_name="users")
    destinations = models.ManyToManyField(Country, blank=True)
    user_languages = models.ManyToManyField(Language, blank=True)
    excluded_origin_countries = models.ManyToManyField(Country, blank=True, related_name="excluded_origins")

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
    immigration_status = models.ManyToManyField(ImmigrationStatus, blank=True)
    total_logged_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Total number of hours the user has been logged in")
    dashboard_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User's dashboard customization preferences"
    )
    dashboard_preferences_version = models.IntegerField(default=1, help_text="Version of dashboard preferences schema")
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="deleted_users"
    )

    class Meta(AuditFieldsMixin.Meta):
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        return f"{self.email}"
    
    def soft_delete(self, deleted_by):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.deleted_by = deleted_by
        self.updated_by = deleted_by
        self.save()
        
    def deactivate(self, deactivated_by):
        self.is_active = False
        self.updated_at = timezone.now()
        self.updated_by = deactivated_by
        self.save()


class UserInvitations(models.Model):
    STATUS = models.TextChoices("Status", " ".join(STATUS))
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="invitations",
    )
    email = models.EmailField(null=True, blank=True, max_length=128)
    role = models.CharField(blank=False, null=True, choices=User.ROLE.choices, max_length=16)
    scheme = models.ForeignKey(to="dashboard.Scheme", on_delete=models.DO_NOTHING, null=True, max_length=16)
    factory = models.ForeignKey(to="dashboard.Factory", on_delete=models.DO_NOTHING, null=True, max_length=16)
    organisation = models.ForeignKey(
        OrganisationData,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="user_invitations",
    )
    phone_number = models.CharField(blank=True, null=True, max_length=32)
    status = models.CharField(
        blank=False, null=False, max_length=16, choices=STATUS.choices, default="PENDING"
    )


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    duration = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        if self.logout_time and not self.duration:
            duration = (self.logout_time - self.login_time).total_seconds() / 3600
            self.duration = Decimal(str(round(duration, 2)))
            
            self.user.total_logged_hours = Decimal(str(self.user.total_logged_hours)) + self.duration
            self.user.save()
        
        super().save(*args, **kwargs)
