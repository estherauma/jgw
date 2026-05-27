from django.test import TestCase
from django.urls import reverse

from preference.models import OrganisationAccessCode, OrganisationData
from user_management.models import WorkGroup
from django.contrib.auth.models import Group
from users.models import User
from users.services.authentication import issue_auth_tokens
from user_management.roles import add_default_org_roles


class AccessCodeDetailsApiTests(TestCase):
    def setUp(self):
        self.organisation = OrganisationData.objects.create(
            name="Test Org",
            org_code="TESTORG",
            display_name="Test Organisation",
            theme="default",
            work_sector="Agriculture",
            content_collection="test-org",
            default_collection_language="en",
        )
        self.access_code = OrganisationAccessCode.objects.create(
            code="TEST123",
            organisation=self.organisation,
            requires_login=True,
        )
        self.worker_group = WorkGroup.objects.create(name="Worker", organisation=self.organisation)
        self.supervisor_group = WorkGroup.objects.create(name="Supervisor", organisation=self.organisation)
        self.access_code.work_groups.add(self.supervisor_group, self.worker_group)
        self.user = User.objects.create_user(
            email="member@example.com",
            password="StrongPassword123!",
            is_active=True,
        )
        self.user.organisation_data.add(self.organisation)
        self.auth_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {issue_auth_tokens(self.user)['access_token']}"
        }

    def test_access_code_details_requires_authentication(self):
        response = self.client.get(
            reverse(
                "user_management_v1_api:access_code_details_api",
                args=("test123",),
            )
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Authentication credentials were not provided.")

    def test_access_code_status_returns_public_response(self):
        response = self.client.get(
            reverse(
                "user_management_v1_api:access_code_status_api",
                args=("test123",),
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "code": "TEST123",
                "requires_login": True,
            },
        )

    def test_access_code_status_returns_404_when_not_found(self):
        response = self.client.get(
            reverse(
                "user_management_v1_api:access_code_status_api",
                args=("missing123",),
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"ok": False, "error": "Access code not found."})


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

    def test_access_code_details_requires_user_to_belong_to_organization(self):
        outsider = User.objects.create_user(
            email="outsider@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        response = self.client.get(
            reverse(
                "user_management_v1_api:access_code_details_api",
                args=("test123",),
            ),
            HTTP_AUTHORIZATION=f"Bearer {issue_auth_tokens(outsider)['access_token']}",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"ok": False, "error": "You do not have access to this organisation."})

    def test_access_code_details_returns_code_org_and_work_groups(self):
        response = self.client.get(
            reverse(
                "user_management_v1_api:access_code_details_api",
                args=("test123",),
            ),
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.access_code.id)
        self.assertEqual(response.json()["code"], "TEST123")
        self.assertEqual(response.json()["requires_login"], True)
        self.assertIsNone(response.json()["expiry_date"])
        self.assertEqual(response.json()["organization"]["id"], self.organisation.id)
        self.assertEqual(response.json()["organization"]["name"], "Test Org")
        self.assertEqual(response.json()["organization"]["org_code"], "TESTORG")
        self.assertEqual(
            response.json()["workgroups"],
            [
                {"id": self.supervisor_group.id, "name": "Supervisor"},
                {"id": self.worker_group.id, "name": "Worker"},
            ],
        )

    def test_access_code_details_returns_404_when_not_found(self):
        response = self.client.get(
            reverse(
                "user_management_v1_api:access_code_details_api",
                args=("missing123",),
            ),
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"ok": False, "error": "Access code not found."})

    def test_access_code_details_returns_404_when_organization_is_soft_deleted(self):
        self.organisation.soft_delete(self.user)

        response = self.client.get(
            reverse(
                "user_management_v1_api:access_code_details_api",
                args=("test123",),
            ),
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"ok": False, "error": "Access code not found."})

    def test_access_code_status_returns_404_when_organization_is_soft_deleted(self):
        self.organisation.soft_delete(self.user)

        response = self.client.get(
            reverse(
                "user_management_v1_api:access_code_status_api",
                args=("test123",),
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"ok": False, "error": "Access code not found."})
