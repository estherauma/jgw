from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from preference.models import OrganisationAccessCode, OrganisationData, SiteLanguages
from user_management.models import WorkGroup
from users.models import User
from users.services.authentication import issue_auth_tokens


class AccessCodeDetailsApiTests(TestCase):
    def setUp(self):
        self.organisation = OrganisationData.objects.create(
            name="Test Org",
            org_code="TESTORG",
            display_name="Test Organisation",
            theme="default",
            custom_type="version_1",
            work_sector="Agriculture",
            content_collection="test-org",
            default_collection_language="en",
            default_feedback_emails="feedback@example.com",
            default_report_issue_emails="report@example.com",
            big_icon="https://cdn.example.com/big.png",
            small_icon="https://cdn.example.com/small.png",
        )
        SiteLanguages.objects.create(
            organisation=self.organisation,
            code="en",
            name="English",
        )
        SiteLanguages.objects.create(
            organisation=self.organisation,
            code="sw",
            name="Swahili",
        )
        self.access_code = OrganisationAccessCode.objects.create(
            code="TEST123",
            organisation=self.organisation,
            requires_login=True,
        )
        self.worker_group = WorkGroup.objects.create(
            name="Worker",
            organisation=self.organisation,
        )
        self.supervisor_group = WorkGroup.objects.create(
            name="Supervisor",
            organisation=self.organisation,
        )
        self.access_code.work_groups.add(self.supervisor_group, self.worker_group)
        self.public_access_code = OrganisationAccessCode.objects.create(
            code="PUBLIC123",
            organisation=self.organisation,
            requires_login=False,
        )
        self.public_access_code.work_groups.add(self.supervisor_group, self.worker_group)
        self.user = User.objects.create_user(
            email="member@example.com",
            password="StrongPassword123!",
            is_active=True,
        )
        self.user.organisation_data.add(self.organisation)
        self.user.work_groups.add(self.worker_group)
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
        self.assertEqual(
            response.json()["detail"],
            "Authentication credentials were not provided.",
        )

    def test_public_access_code_details_can_be_fetched_without_authentication(self):
        response = self.client.get(
            reverse(
                "user_management_v1_api:access_code_details_api",
                args=("public123",),
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.public_access_code.id)
        self.assertEqual(response.json()["code"], "PUBLIC123")
        self.assertEqual(response.json()["requires_login"], False)
        self.assertEqual(response.json()["organization"]["id"], self.organisation.id)
        self.assertEqual(
            response.json()["access_code_user_groups"],
            [
                {"id": self.supervisor_group.id, "name": "Supervisor"},
                {"id": self.worker_group.id, "name": "Worker"},
            ],
        )

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
        self.assertEqual(
            response.json(),
            {"ok": False, "error": "You do not have access to this organisation."},
        )

    def test_access_code_details_returns_code_org_and_user_groups(self):
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
        self.assertEqual(response.json()["organization"]["has_custom_content"], True)
        self.assertEqual(response.json()["organization"]["theme"], "default")
        self.assertEqual(response.json()["organization"]["custom_type"], "version_1")
        self.assertEqual(
            response.json()["organization"]["default_feedback_emails"],
            "feedback@example.com",
        )
        self.assertEqual(
            response.json()["organization"]["default_report_issue_emails"],
            "report@example.com",
        )
        self.assertCountEqual(
            response.json()["organization"]["collection_languages"],
            [
                {"code": "en", "name": "English"},
                {"code": "sw", "name": "Swahili"},
            ],
        )
        self.assertEqual(
            response.json()["organization"]["big_icon_url"],
            "https://cdn.example.com/big.png",
        )
        self.assertEqual(
            response.json()["organization"]["small_icon_url"],
            "https://cdn.example.com/small.png",
        )
        self.assertEqual(
            response.json()["access_code_user_groups"],
            [
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


@override_settings(EXTERNAL_API_KEY="external-secret")
class PartnerConfigApiTests(TestCase):
    def setUp(self):
        self.organisation = OrganisationData.objects.create(
            name="Partner Org",
            org_code="PARTNER1",
            display_name="Partner Organisation",
            theme="default",
            custom_type="version_1",
            work_sector="Agriculture",
            content_collection="partner-org",
            default_collection_language="en",
            default_feedback_emails="feedback@example.com",
            default_report_issue_emails="report@example.com",
            big_icon="https://cdn.example.com/big.png",
            small_icon="https://cdn.example.com/small.png",
        )
        SiteLanguages.objects.create(
            organisation=self.organisation,
            code="en",
            name="English",
        )
        self.access_code = OrganisationAccessCode.objects.create(
            code="PARTNER123",
            organisation=self.organisation,
            requires_login=True,
        )
        self.public_access_code = OrganisationAccessCode.objects.create(
            code="PARTNERPUB",
            organisation=self.organisation,
            requires_login=False,
        )
        self.worker_group = WorkGroup.objects.create(
            name="Worker",
            organisation=self.organisation,
        )
        self.supervisor_group = WorkGroup.objects.create(
            name="Supervisor",
            organisation=self.organisation,
        )

    def test_partner_configs_requires_api_key(self):
        response = self.client.get(
            reverse("user_management_v1_api:partner_configs_api")
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "API key was not provided.")

    def test_partner_configs_rejects_invalid_api_key(self):
        response = self.client.get(
            reverse("user_management_v1_api:partner_configs_api"),
            HTTP_X_API_KEY="wrong-key",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid API key.")

    def test_partner_configs_returns_all_organizations_payload(self):
        another_org = OrganisationData.objects.create(
            name="Zed Org",
            org_code="ZED1",
            display_name="Zed Organisation",
        )

        response = self.client.get(
            reverse("user_management_v1_api:partner_configs_api"),
            HTTP_X_API_KEY="external-secret",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()[0]["id"], self.organisation.id)
        self.assertEqual(response.json()[0]["org_code"], "PARTNER1")
        self.assertEqual(response.json()[0]["display_name"], "Partner Organisation")
        self.assertEqual(response.json()[0]["has_custom_content"], True)
        self.assertEqual(response.json()[0]["theme"], "default")
        self.assertEqual(response.json()[0]["custom_type"], "version_1")
        self.assertEqual(response.json()[0]["work_sector"], "Agriculture")
        self.assertEqual(response.json()[0]["content_collection"], "partner-org")
        self.assertEqual(response.json()[0]["default_collection_language"], "en")
        self.assertEqual(
            response.json()[0]["default_feedback_emails"],
            "feedback@example.com",
        )
        self.assertEqual(
            response.json()[0]["default_report_issue_emails"],
            "report@example.com",
        )
        self.assertEqual(
            response.json()[0]["collection_languages"],
            [{"code": "en", "name": "English"}],
        )
        self.assertEqual(
            response.json()[0]["access_codes"],
            [
                {
                    "id": self.access_code.id,
                    "code": "PARTNER123",
                    "requires_login": True,
                    "expiry_date": None,
                },
                {
                    "id": self.public_access_code.id,
                    "code": "PARTNERPUB",
                    "requires_login": False,
                    "expiry_date": None,
                },
            ],
        )
        self.assertCountEqual(
            response.json()[0]["user_groups"],
            [
                {"id": self.supervisor_group.id, "name": "Supervisor"},
                {"id": self.worker_group.id, "name": "Worker"},
            ],
        )
        self.assertEqual(
            response.json()[0]["big_icon_url"],
            "https://cdn.example.com/big.png",
        )
        self.assertEqual(
            response.json()[0]["small_icon_url"],
            "https://cdn.example.com/small.png",
        )
        self.assertEqual(response.json()[1]["id"], another_org.id)

    def test_partner_configs_excludes_soft_deleted_organizations(self):
        self.organisation.is_deleted = True
        self.organisation.save(update_fields=["is_deleted"])

        response = self.client.get(
            reverse("user_management_v1_api:partner_configs_api"),
            HTTP_X_API_KEY="external-secret",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
