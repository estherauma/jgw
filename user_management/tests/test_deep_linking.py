from unittest.mock import Mock, patch

import requests
from django.test import TestCase, override_settings
from django.urls import reverse

from preference.models import OrganisationAccessCode, OrganisationData
from user_management.services.deep_links import DeepLinkService
from users.models import User

TEST_BRANCH_DOMAIN = "branch.test.local"


class DeepLinkServiceTests(TestCase):
    def setUp(self):
        self.organisation = OrganisationData.objects.create(
            name="Bar Way",
            org_code="BARWAY",
            display_name="Bar Way",
            theme="default",
            custom_type="version_1",
            work_sector="Agriculture",
            content_collection="bar-way",
            default_collection_language="en",
            default_feedback_emails="feedback@example.com",
            default_report_issue_emails="report@example.com",
            big_icon="https://cdn.example.com/big.png",
            small_icon="https://cdn.example.com/small.png",
        )
        self.work_code = OrganisationAccessCode.objects.create(
            code="BAR123",
            organisation=self.organisation,
            requires_login=True,
        )

    def test_get_conflicting_branch_url_returns_conflict_url(self):
        conflict_url = DeepLinkService.get_conflicting_branch_url(
            response_data={
                "error": {
                    "code": 400,
                    "message": f"Link alias conflict: {TEST_BRANCH_DOMAIN}/barway-132",
                }
            }
        )

        self.assertEqual(
            conflict_url,
            f"{TEST_BRANCH_DOMAIN}/barway-132",
        )

    def test_get_conflicting_branch_url_returns_none_for_non_conflict_error(self):
        conflict_url = DeepLinkService.get_conflicting_branch_url(
            response_data={
                "error": {
                    "code": 400,
                    "message": "Some other Branch validation error",
                }
            }
        )

        self.assertIsNone(conflict_url)


    @override_settings(
        BRANCH_KEY="branch-key",
        BRANCH_LINK_DOMAIN=TEST_BRANCH_DOMAIN,
    )
    @patch("user_management.services.deep_links.requests.post")
    def test_create_branch_deep_link_returns_conflicting_url_on_alias_conflict(
        self, mock_post
    ):
        mock_response = Mock()
        mock_response.ok = False
        mock_response.json.return_value = {
            "error": {
                "code": 400,
                "message": f"Link alias conflict: {TEST_BRANCH_DOMAIN}/barway-132",
            }
        }
        mock_response.text = '{"error":{"code":400,"message":"Link alias conflict"}}'
        mock_post.return_value = mock_response

        branch_url = DeepLinkService.create_branch_deep_link(
            payload={"alias": "barway-132"}
        )

        self.assertEqual(branch_url, f"{TEST_BRANCH_DOMAIN}/barway-132")


    @patch("user_management.services.deep_links.DeepLinkService.create_qr_code")
    @patch("user_management.services.deep_links.DeepLinkService.create_branch_deep_link")
    def test_get_or_create_login_deep_link_uses_existing_saved_url(
        self, mock_create_branch_deep_link, mock_create_qr_code
    ):
        self.work_code.deep_link = "https://existing.example/link"
        self.work_code.save(update_fields=["deep_link", "updated_at"])
        mock_create_qr_code.return_value = "data:image/svg+xml;base64,qr"

        result = DeepLinkService.get_or_create_login__deep_link(work_code=self.work_code)

        self.assertEqual(
            result,
            {
                "url": "https://existing.example/link",
                "qr_code_url": "data:image/svg+xml;base64,qr",
            },
        )
        mock_create_branch_deep_link.assert_not_called()
        mock_create_qr_code.assert_called_once_with(
            deep_link="https://existing.example/link"
        )

    @patch("user_management.services.deep_links.DeepLinkService.create_qr_code")
    @patch("user_management.services.deep_links.DeepLinkService.create_branch_deep_link")
    def test_get_or_create_login_deep_link_creates_and_saves_branch_url(
        self, mock_create_branch_deep_link, mock_create_qr_code
    ):
        mock_create_branch_deep_link.return_value = "https://branch.example/generated"
        mock_create_qr_code.return_value = "data:image/svg+xml;base64,qr"

        result = DeepLinkService.get_or_create_login__deep_link(work_code=self.work_code)

        self.work_code.refresh_from_db()
        self.assertEqual(self.work_code.deep_link, "https://branch.example/generated")
        self.assertEqual(result["url"], "https://branch.example/generated")
        self.assertEqual(result["qr_code_url"], "data:image/svg+xml;base64,qr")
        mock_create_branch_deep_link.assert_called_once_with(
            payload={
                "alias": f"bar-way-{self.work_code.id}",
                "feature": "login",
                "campaign": "user_management",
                "tags": ["Bar Way"],
                "data": {
                    "$marketing_title": "Bar Way - Login ",
                    "type": "login",
                    "organisationAccessCode": "BAR123",
                },
            }
        )


class CreateDeepLinkViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="deep-linker@example.com",
            password="StrongPassword123!",
            is_active=True,
        )
        self.client.force_login(self.user)
        self.url = reverse("user_management:create_deep_link")

    def test_returns_400_for_invalid_json_payload(self):
        response = self.client.post(
            self.url,
            data="{invalid json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"ok": False, "error": "Invalid JSON payload."},
        )

    def test_returns_400_for_unsupported_deep_link_type(self):
        response = self.client.post(
            self.url,
            data='{"work_code_id": 1, "link_type": "invite"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"ok": False, "error": "Unsupported deep link type."},
        )

    @patch("user_management.views.web.OrganizationService.create_login_deep_link")
    def test_returns_generated_deep_link_payload(self, mock_create_login_deep_link):
        mock_create_login_deep_link.return_value = {
            "url": "https://branch.example/generated",
            "qr_code_url": "data:image/svg+xml;base64,qr",
        }

        response = self.client.post(
            self.url,
            data='{"work_code_id": 7, "link_type": "login"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "ok": True,
                "url": "https://branch.example/generated",
                "qr_code_url": "data:image/svg+xml;base64,qr",
                "data": {
                    "url": "https://branch.example/generated",
                    "qr_code_url": "data:image/svg+xml;base64,qr",
                },
            },
        )
        mock_create_login_deep_link.assert_called_once()

    @patch("user_management.views.web.OrganizationService.create_login_deep_link")
    def test_returns_400_for_service_value_error(self, mock_create_login_deep_link):
        mock_create_login_deep_link.side_effect = ValueError("Work code is required.")

        response = self.client.post(
            self.url,
            data='{"link_type": "login"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"ok": False, "error": "Work code is required."},
        )

    @patch("user_management.views.web.OrganizationService.create_login_deep_link")
    def test_returns_403_for_permission_error(self, mock_create_login_deep_link):
        mock_create_login_deep_link.side_effect = PermissionError(
            "You do not have access to this organisation."
        )

        response = self.client.post(
            self.url,
            data='{"work_code_id": 7, "type": "login"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(),
            {"ok": False, "error": "You do not have access to this organisation."},
        )

    @patch("user_management.views.web.OrganizationService.create_login_deep_link")
    def test_returns_500_for_unexpected_error(self, mock_create_login_deep_link):
        mock_create_login_deep_link.side_effect = RuntimeError("boom")

        response = self.client.post(
            self.url,
            data='{"work_code_id": 7, "type": "login"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {
                "ok": False,
                "error": "An error occurred while generating the deep link. Please try again.",
            },
        )
