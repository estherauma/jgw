from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0005_remove_appuser"),
        ("preference", "0048_auto_20260311_0647"),
        ("waffle", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="OrganisationRole",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("description", models.TextField(blank=True)),
                ("grants_dashboard_access", models.BooleanField(default=False)),
                ("is_system", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roles",
                        to="preference.organisationdata",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OrganisationRoleAssignment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="role_assignments",
                        to="preference.organisationdata",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignments",
                        to="user_management.organisationrole",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="org_roles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OrganisationRolePermission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "flag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="role_permissions",
                        to="waffle.flag",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="role_permissions",
                        to="user_management.organisationrole",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="organisationrole",
            constraint=models.UniqueConstraint(
                fields=("organisation", "name"),
                name="unique_role_name_per_org",
            ),
        ),
        migrations.AddConstraint(
            model_name="organisationrolepermission",
            constraint=models.UniqueConstraint(
                fields=("role", "flag"),
                name="unique_role_flag_permission",
            ),
        ),
        migrations.AddConstraint(
            model_name="organisationroleassignment",
            constraint=models.UniqueConstraint(
                fields=("user", "organisation"),
                name="unique_role_assignment_per_org",
            ),
        ),
    ]
