from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from preference.models import OrganisationData
from user_management.models import WorkGroup
from user_management.roles import add_default_org_roles
from users.models import User


class DashboardUserManagementTests(TestCase):
    def test_edit_dashboard_user_preserves_is_active_when_field_is_missing(self):
        admin_user = User.objects.create_user(
            email="admin@example.com",
            password="StrongPassword123!",
            is_active=True,
            is_superuser=True,
            is_staff=True,
            access_type="dashboard",
        )
        target_user = User.objects.create_user(
            email="target@example.com",
            password="StrongPassword123!",
            is_active=True,
            access_type="dashboard",
            first_name="Target",
            last_name="User",
        )
        admin_group = Group.objects.create(name="58_admin")
        self.client.force_login(admin_user)

        response = self.client.post(
            reverse("user_management:edit_dashboard_user", args=(target_user.id,)),
            data={
                "email": "target@example.com",
                "first_name": "Updated",
                "last_name": "User",
                "groups": [admin_group.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        target_user.refresh_from_db()
        self.assertTrue(target_user.is_active)
        self.assertEqual(target_user.first_name, "Updated")

    def test_edit_app_user_preserves_is_active_for_existing_worker(self):
        admin_user = User.objects.create_user(
            email="admin@example.com",
            password="StrongPassword123!",
            is_active=True,
            is_superuser=True,
            is_staff=True,
            access_type="dashboard",
        )
        organisation = OrganisationData.objects.create(name="Test Org", org_code="TESTORG")
        worker_role = next(
            role for role in add_default_org_roles(organisation)
            if role.name == "Worker"
        )
        target_user = User.objects.create_user(
            email="worker@example.com",
            password="StrongPassword123!",
            is_active=True,
            access_type="app",
            first_name="Worker",
            last_name="User",
        )
        target_user.organisation_data.add(organisation)
        work_group = WorkGroup.objects.create(name="Worker Group", organisation=organisation)
        self.client.force_login(admin_user)

        response = self.client.post(
            reverse("user_management:edit_app_user", args=(target_user.id,)),
            data={
                "email": "worker@example.com",
                "first_name": "Updated",
                "last_name": "User",
                "role": worker_role.id,
                "work_groups": [work_group.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        target_user.refresh_from_db()
        self.assertTrue(target_user.is_active)
        self.assertEqual(target_user.first_name, "Updated")

