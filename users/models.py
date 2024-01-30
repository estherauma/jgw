from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from dashboard.forms import OPERATORS
from preference.models import Country, FactoryFarm, Language, Organisation

ROLES = ["SCHEME", "FACTORY", "STAFF", "ADMIN"]
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


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name_plural = "Users"

    objects = UserManager()
    USERNAME_FIELD = "email"
    ROLE = models.TextChoices("Role", " ".join(ROLES))

    password = models.CharField(blank=True, max_length=128)
    first_name = models.CharField(blank=True, null=False, max_length=128)
    last_name = models.CharField(blank=True, null=False, max_length=128)
    role = models.CharField(blank=True, null=True, choices=ROLE.choices, max_length=16)
    scheme = models.ForeignKey(
        to="dashboard.Scheme", on_delete=models.DO_NOTHING, null=True, max_length=16, blank=True
    )
    email = models.EmailField(null=False, blank=False, max_length=128, unique=True)

    factories = models.ManyToManyField(FactoryFarm, blank=True)
    organisations = models.ManyToManyField(Organisation, blank=True)
    destinations = models.ManyToManyField(Country, blank=True)
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

    def __str___(self):
        return f"{self.email}"


class UserInvitations(models.Model):
    STATUS = models.TextChoices("Status", " ".join(STATUS))
    email = models.EmailField(null=False, blank=False, max_length=128)
    role = models.CharField(blank=False, null=True, choices=User.ROLE.choices, max_length=16)
    scheme = models.ForeignKey(to="dashboard.Scheme", on_delete=models.DO_NOTHING, null=True, max_length=16)
    factory = models.ForeignKey(to="dashboard.Factory", on_delete=models.DO_NOTHING, null=True, max_length=16)
    organisation = models.CharField(max_length=64, null=True, blank=False, choices=OPERATORS.items())
    status = models.CharField(
        blank=False, null=False, max_length=16, choices=STATUS.choices, default="PENDING"
    )
