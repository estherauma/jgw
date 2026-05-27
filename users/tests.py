from datetime import datetime, timedelta, timezone

import jwt
from unittest.mock import patch
from django.conf import settings
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from dashboard.models import Factory, Scheme
from preference.models import OrganisationData
from user_management.models import WorkGroup
from users.services.authentication import (
    REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
    create_registration_verification_code,
)

from .forms import (
    APIAppUserForm,
    APIDashboardUserForm,
    ChangeEmailForm,
    CreateUserForm,
    InviteUserForm,
    SetPasswordForm,
    UserMgtForm,
)
from .models import User, UserInvitations, UserVerificationCode
from django.utils.translation import gettext as _


class AuthTests(TestCase):
    def setUp(self) -> None:
        super(AuthTests, self).setUp()
        self.test_email = "test@test.local"
        self.test_pword = "12t32thome"
        self.test_scheme = Scheme.objects.create(name="Test_Scheme")
        self.test_user = User.objects.create_user(
            email=self.test_email,
            password=self.test_pword,
            is_active=True,
            scheme=self.test_scheme,
            is_staff=True,
        )
        self.client.login(email=self.test_user, password=self.test_pword)
        self.factory = Factory.objects.create(name="Test_Factory")
        expiry = datetime.now(tz=timezone.utc) + timedelta(days=1)
        self.pword_reset_token = jwt.encode(
            payload={"exp": expiry, "user_id": self.test_user.id}, key=settings.SECRET_KEY
        )
        self.test_user_2 = User.objects.create_user(
            email="test2@test.com",
            password=self.test_pword,
            is_active=True,
            scheme=self.test_scheme,
        )

    def test_authorisation(self):
        """
        Test dashboard views require email/pword login to access
        """
        self.client.logout()
        response = self.client.get(reverse("dashboard:preferences"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/preferences")
        response = self.client.get(reverse("dashboard:inline"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/inline")

    def test_signup_OK(self):
        response = self.client.post(
            reverse("users:create_user"),
            {"email": "test2@test.local", "password1": self.test_pword, "password2": self.test_pword},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("users:login_user"))

    def test_signup_form_validation(self):
        """
        Test sign up form validation
        """
        response = self.client.post(
            reverse("users:create_user"),
            {"email": self.test_email, "password1": self.test_pword, "password2": ""},
        )
        form_errors = dict(response.context["form"].errors)
        self.assertTrue(bool(form_errors))
        self.assertEqual(
            form_errors,
            {"password2": ["This field is required."], "email": ["User with this Email already exists."]},
        )

    def test_login_OK(self):
        response = self.client.post(
            reverse("users:login_user"), {"email": self.test_email, "password": self.test_pword}
        )
        self.assertEqual(response.status_code, 302)

    def test_worker_user_login_is_blocked_from_dashboard_ui(self):
        worker_group, _ = Group.objects.get_or_create(name="worker")
        worker_user = User.objects.create_user(
            email="worker@test.local",
            password=self.test_pword,
            is_active=True,
            scheme=self.test_scheme,
            access_type="app",
        )
        worker_user.groups.add(worker_group)

        response = self.client.post(
            reverse("users:login_user"),
            {"email": "worker@test.local", "password": self.test_pword},
        )

        self.assertEqual(response.status_code, 200)
        messages = [str(i) for i in response.context["messages"]]
        self.assertEqual(
            messages,
            ["This account is not allowed to access the dashboard."],
        )
        self.assertNotIn("user_id", self.client.session)

    def test_login_form_validation(self):
        """
        Test login form validation
        """
        response = self.client.post(
            reverse("users:login_user"), {"email": "test2@test.local", "password": self.test_pword}
        )
        messages = [str(i) for i in response.context["messages"]]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(messages, [_("loginUserViewErrorNotUser")])
        response = self.client.post(
            reverse("users:login_user"), {"email": "test@fakeemail.", "password": self.test_pword}
        )
        form_errors = dict(response.context["form"].errors)
        self.assertEqual(form_errors, {"email": [_("loginFormEmailInvalid")]})

    def test_invite_user_view_renders_correctly(self):
        response = self.client.get(reverse("users:invite_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/invite_user.html")
        self.assertIsInstance(response.context["form"], InviteUserForm)

    @patch("users.tasks.send_email_notification.delay")
    def test_invite_user_OK(self, mock_send_email):
        response = self.client.post(
            reverse("users:invite_user"),
            {
                "email": "test_invite@test.local",
                "role": "SCHEME",
                "scheme": Scheme.objects.first().id,
                "factory": Factory.objects.first().id,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/")
        self.assertEqual(len(UserInvitations.objects.all()), 1)

    def test_invite_user_form_rejects_existing_user_email(self):
        response = self.client.post(
            reverse("users:invite_user"),
            {
                "email": "test@test.local",
                "role": "SCHEME",
                "scheme": Scheme.objects.first().id,
                "factory": Factory.objects.first().id,
            },
        )
        self.assertEqual(len(response.context["form"].errors.values()), 1)
        self.assertEqual(
            dict(response.context["form"].errors),
            {"__all__": ["An account with this email address already exists!"]},
        )

    def test_manage_user_view_renders_correctly(self):
        response = self.client.get(reverse("users:manage_user", args=(self.test_user.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/manage_user.html")
        self.assertIsInstance(response.context["form"], UserMgtForm)

    def test_manage_user_OK(self):
        new_user = User.objects.create_user(email="test2@test.local", password=self.test_pword)
        response = self.client.post(reverse("users:manage_user", args=(new_user.id,)), {"is_active": True})
        form_errors = dict(response.context["form"].errors)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form_errors, {})
        new_user = User.objects.get(email="test2@test.local")
        self.assertTrue(new_user.is_active)

    @patch("users.tasks.send_email_notification.delay")
    def test_activate_user_OK(self, mock_send_email):
        new_user = User.objects.create_user(email="test2@test.local", password=self.test_pword)
        response = self.client.get(reverse("users:activate_account", args=(new_user.id,)))
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(email="test2@test.local")
        self.assertTrue(new_user.is_active)
        expected_url = reverse('users:list_users') + "?page=1&items_per_page=25"
        self.assertRedirects(response, expected_url)

    @patch("users.tasks.send_email_notification.delay")
    def test_deactivate_user_OK(self, mock_send_email):
        new_user = User.objects.create_user(
            email="test2@test.local", password=self.test_pword, is_active=True
        )
        response = self.client.get(reverse("users:activate_account", args=(new_user.id,)))
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(email="test2@test.local")
        self.assertFalse(new_user.is_active)
        expected_url = reverse('users:list_users') + "?page=1&items_per_page=25"
        self.assertRedirects(response, expected_url)

    def test_create_user_view_renders_correctly(self):
        response = self.client.get(reverse("users:create_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up.html")
        self.assertIsInstance(response.context["form"], CreateUserForm)

    def test_list_users_view_renders_correctly(self):
        response = self.client.get(reverse("users:list_users"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/list_users.html")

    def test_list_users_view_non_admin(self):
        self.client.logout()
        self.client.login(email=self.test_user_2, password=self.test_pword)

        response = self.client.get(reverse("users:list_users"))

        self.assertEqual(response.status_code, 403)

    def test_verify_invite_view_OK(self):
        invite_data = {
            "email": "test_invite@test.local",
            "role": "SCHEME",
            "scheme_id": Scheme.objects.first().id,
            "factory_id": Factory.objects.first().id,
        }
        invite = UserInvitations.objects.create(**invite_data)
        payload = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "invite_id": invite.id,
        }
        invite_token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.get(reverse("users:verify_invite", args=(invite_token,)))
        self.assertEqual(response.status_code, 302)
        invite = UserInvitations.objects.first()
        self.assertEqual(invite.status, "ACCEPTED")

    def test_verify_invite_view_expired_token(self):
        invite_data = {
            "email": "test_invite@test.local",
            "role": "SCHEME",
            "scheme_id": Scheme.objects.first().id,
            "factory_id": Factory.objects.first().id,
        }
        invite = UserInvitations.objects.create(**invite_data)
        payload = {
            "exp": datetime.now(tz=timezone.utc) - timedelta(days=1),
            "invite_id": invite.id,
        }
        invite_token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.get(reverse("users:verify_invite", args=(invite_token,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["messages"])[0].message, "This link is expired!")

    def test_verify_invite_view_invalid_invitation(self):
        payload = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "invite_id": 3,
        }
        invite_token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.get(reverse("users:verify_invite", args=(invite_token,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["messages"])[0].message, "Invitation not found!")

    def test_set_password_view_renders_correctly(self):
        response = self.client.get(reverse("users:set_password", args=(self.pword_reset_token,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/set_password.html")
        self.assertIsInstance(response.context["form"], SetPasswordForm)


class RegistrationApiTests(TestCase):
    def setUp(self):
        self.organisation = OrganisationData.objects.create(
            name="Test Org",
            org_code="TESTORG",
        )

    @patch("users.api_views.initialize_user_dashboard_preferences")
    @patch("users.api_views.send_registration_verification_email")
    def test_register_user_sends_verification_email(self, send_email_mock, init_prefs_mock):
        with patch(
            "users.services.authentication.generate_registration_verification_code",
            return_value="AB23CD45",
        ):
            response = self.client.post(
                reverse("user_management_api:register_user_api"),
                data={
                    "first_name": "New",
                    "last_name": "User",
                    "email": "newuser@example.com",
                    "password1": "StrongPassword123!",
                    "org_code": "TESTORG",
                },
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["ok"], True)
        user = User.all_objects.get(email="newuser@example.com")
        self.assertEqual(response.json()["user_id"], user.id)
        self.assertEqual(response.json()["email"], "newuser@example.com")
        self.assertIsNone(response.json()["phone_number"])
        self.assertIsNone(response.json()["phone_country_iso"])
        self.assertFalse(user.is_active)
        self.assertEqual(user.access_type, "app")
        self.assertTrue(user.check_password("StrongPassword123!"))
        self.assertTrue(user.organisation_data.filter(id=self.organisation.id).exists())
        verification = UserVerificationCode.objects.get(
            user=user,
            purpose=REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
        )
        self.assertEqual(len(verification.code_hash) > 0, True)
        worker_group = Group.objects.get(name="worker")
        self.assertTrue(user.groups.filter(id=worker_group.id).exists())
        init_prefs_mock.assert_not_called()
        send_email_mock.assert_called_once()
        send_email_mock.assert_called_once_with(user, "AB23CD45")

    @patch("users.api_views.send_registration_verification_email")
    def test_register_user_returns_validation_errors(self, send_email_mock):
        response = self.client.post(
            reverse("user_management_api:register_user_api"),
            data={
                "first_name": "New",
                "last_name": "User",
                "org_code": "TESTORG",
                "password1": "StrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["ok"], False)
        self.assertIn("__all__", response.json()["errors"])
        self.assertIn(
            "Provide either an email or phone number for app users.",
            response.json()["errors"]["__all__"],
        )
        self.assertFalse(User.all_objects.filter(email="newuser@example.com").exists())
        send_email_mock.assert_not_called()

    @patch("users.api_views.send_registration_verification_email")
    def test_register_user_requires_first_and_last_name(self, send_email_mock):
        response = self.client.post(
            reverse("user_management_api:register_user_api"),
            data={
                "email": "newuser@example.com",
                "password1": "StrongPassword123!",
                "org_code": "TESTORG",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["ok"], False)
        self.assertIn("first_name", response.json()["errors"])
        self.assertIn("last_name", response.json()["errors"])
        send_email_mock.assert_not_called()

    @patch("users.api_views.initialize_user_dashboard_preferences")
    @patch("users.api_views.send_registration_verification_email")
    def test_register_user_respects_provided_access_type(self, send_email_mock, init_prefs_mock):
        with patch(
            "users.services.authentication.generate_registration_verification_code",
            return_value="AB23CD45",
        ):
            response = self.client.post(
                reverse("user_management_api:register_user_api"),
                data={
                    "first_name": "Dashboard",
                    "last_name": "User",
                    "email": "dashboarduser@example.com",
                    "password1": "StrongPassword123!",
                    "access_type": "dashboard",
                },
            )

        self.assertEqual(response.status_code, 201)
        user = User.all_objects.get(email="dashboarduser@example.com")
        self.assertEqual(user.access_type, "dashboard")
        init_prefs_mock.assert_called_once()
        send_email_mock.assert_called_once()

    @patch("users.api_views.initialize_user_dashboard_preferences")
    @patch("users.api_views.send_registration_verification_email")
    def test_verify_registration_code_activates_user(self, send_email_mock, init_prefs_mock):
        with patch(
            "users.services.authentication.generate_registration_verification_code",
            return_value="AB23CD45",
        ):
            self.client.post(
                reverse("user_management_api:register_user_api"),
                data={
                    "first_name": "Verify",
                    "last_name": "Me",
                    "email": "verifyme@example.com",
                    "password1": "StrongPassword123!",
                    "org_code": "TESTORG",
                },
            )

        user = User.all_objects.get(email="verifyme@example.com")
        verification = UserVerificationCode.objects.get(
            user=user,
            purpose=REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
        )
        self.assertIsNone(verification.used_at)

        response = self.client.post(
            reverse("user_management_api:verify_registration_code"),
            data={"email": "verifyme@example.com", "code": "AB23CD45"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ok"], True)
        user.refresh_from_db()
        verification.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertIsNotNone(verification.used_at)

    @patch("users.api_views.send_registration_verification_sms")
    def test_register_app_user_with_phone_only_sends_sms(self, send_sms_mock):
        send_sms_mock.return_value = True
        with patch(
            "users.services.authentication.generate_registration_verification_code",
            return_value="AB23CD45",
        ):
            response = self.client.post(
                reverse("user_management_api:register_user_api"),
                data={
                    "first_name": "Phone",
                    "last_name": "Only",
                    "phone_number": "771234567",
                    "phone_country_iso": "UG",
                    "password1": "StrongPassword123!",
                    "org_code": "TESTORG",
                },
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["ok"], True)
        user = User.all_objects.get(phone_number="+256771234567")
        self.assertEqual(response.json()["user_id"], user.id)
        self.assertIsNone(response.json()["email"])
        self.assertEqual(response.json()["phone_number"], "+256771234567")
        self.assertEqual(response.json()["phone_country_iso"], "UG")
        self.assertEqual(user.access_type, "app")
        send_sms_mock.assert_called_once()

    def test_verify_registration_code_rejects_expired_code(self):
        user = User.objects.create_user(
            email="verifyme@example.com",
            password="StrongPassword123!",
            is_active=False,
        )
        UserVerificationCode.objects.create(
            user=user,
            purpose=REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
            code_hash="pbkdf2_sha256$260000$invalid$hash",
            expires_at=user.created_at,
        )

        response = self.client.post(
            reverse("user_management_api:verify_registration_code"),
            data={"email": "verifyme@example.com", "code": "BADCODE2"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["ok"], False)
        self.assertIn("expired", response.json()["error"].lower())
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    @patch("users.services.authentication.generate_registration_verification_code", return_value="AB23CD45")
    def test_verify_registration_code_rejects_wrong_code(self, _code_mock):
        user = User.objects.create_user(
            email="wrongcode@example.com",
            password="StrongPassword123!",
            is_active=False,
        )
        create_registration_verification_code(user)

        response = self.client.post(
            reverse("user_management_api:verify_registration_code"),
            data={"email": "wrongcode@example.com", "code": "ZZ99YY88"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["ok"], False)
        self.assertIn("invalid", response.json()["error"].lower())

    def test_verify_registration_code_adds_worker_group_for_app_user(self):
        user = User.objects.create_user(
            email="appuser@example.com",
            password="StrongPassword123!",
            is_active=False,
            access_type="app",
        )
        _, verification_code = create_registration_verification_code(user)

        response = self.client.post(
            reverse("user_management_api:verify_registration_code"),
            data={"email": "appuser@example.com", "code": verification_code},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ok"], True)
        worker_group = Group.objects.get(name="worker")
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.groups.filter(id=worker_group.id).exists())

    @patch("users.api_views.send_registration_verification_sms")
    def test_verify_registration_code_accepts_phone_number(self, send_sms_mock):
        send_sms_mock.return_value = True
        with patch(
            "users.services.authentication.generate_registration_verification_code",
            return_value="AB23CD45",
        ):
            self.client.post(
                reverse("user_management_api:register_user_api"),
                data={
                    "first_name": "Phone",
                    "last_name": "Verify",
                    "phone_number": "771234568",
                    "phone_country_iso": "UG",
                    "password1": "StrongPassword123!",
                    "org_code": "TESTORG",
                },
            )

        user = User.all_objects.get(phone_number="+256771234568")
        response = self.client.post(
            reverse("user_management_api:verify_registration_code"),
            data={"phone_number": user.phone_number, "code": "AB23CD45"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ok"], True)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @patch("users.api_views.send_registration_verification_sms")
    def test_verify_registration_code_requires_country_iso_for_local_phone(self, send_sms_mock):
        send_sms_mock.return_value = True
        with patch(
            "users.services.authentication.generate_registration_verification_code",
            return_value="AB23CD45",
        ):
            self.client.post(
                reverse("user_management_api:register_user_api"),
                data={
                    "first_name": "Phone",
                    "last_name": "User",
                    "phone_number": "781590903",
                    "phone_country_iso": "UG",
                    "password1": "StrongPassword123!",
                    "org_code": "TESTORG",
                },
            )

        response = self.client.post(
            reverse("user_management_api:verify_registration_code"),
            data={
                "phone_number": "0781590903",
                "code": "AB23CD45",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["ok"], False)
        self.assertEqual(response.json()["error"], "Select a country code.")

    @patch("users.services.authentication.send_registration_verification_email")
    @patch("users.services.authentication.generate_registration_verification_code", return_value="ZX12CV")
    def test_resend_registration_code_by_email(self, _code_mock, send_email_mock):
        user = User.objects.create_user(
            email="resend@example.com",
            password="StrongPassword123!",
            is_active=False,
        )

        response = self.client.post(
            reverse("user_management_api:resend_registration_code"),
            data={"user_id": user.id, "email": "resend@example.com"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ok"], True)
        self.assertEqual(response.json()["user_id"], user.id)
        self.assertEqual(response.json()["email"], "resend@example.com")
        self.assertIsNone(response.json()["phone_number"])
        self.assertIsNone(response.json()["phone_country_iso"])
        send_email_mock.assert_called_once_with(user, "ZX12CV")

    @patch("users.services.authentication.send_registration_verification_sms")
    @patch("users.services.authentication.generate_registration_verification_code", return_value="ZX12CV")
    def test_resend_registration_code_by_local_phone(self, _code_mock, send_sms_mock):
        send_sms_mock.return_value = True
        user = User(
            is_active=False,
            access_type="app",
            phone_number="+256700000000",
            phone_country_iso="UG",
        )
        user.set_password("StrongPassword123!")
        user.save()

        response = self.client.post(
            reverse("user_management_api:resend_registration_code"),
            data={
                "user_id": user.id,
                "phone_number": "0700000000",
                "phone_country_iso": "UG",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ok"], True)
        self.assertEqual(response.json()["user_id"], user.id)
        self.assertIsNone(response.json()["email"])
        self.assertEqual(response.json()["phone_number"], "+256700000000")
        self.assertEqual(response.json()["phone_country_iso"], "UG")
        send_sms_mock.assert_called_once_with(user, "ZX12CV")

    def test_resend_registration_code_requires_identifier(self):
        response = self.client.post(
            reverse("user_management_api:resend_registration_code"),
            data={},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["ok"], False)
        self.assertEqual(response.json()["error"], "Provide a user ID, email or phone number.")


class LoginApiTests(AuthTests):
    def setUp(self):
        super().setUp()
        self.password = "StrongPassword123!"
        self.user = User.objects.create_user(
            email="login@example.com",
            password=self.password,
            is_active=True,
            access_type="dashboard",
        )

    def test_login_api_returns_tokens_and_updates_last_login(self):
        self.assertIsNone(self.user.last_login)
        response = self.client.post(
            reverse("user_management_api:login_api"),
            data={
                "email": "login@example.com",
                "password": self.password,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ok"], True)
        self.assertEqual(
            set(response.json().keys()),
            {"ok", "access_token", "refresh_token"},
        )
        self.assertTrue(response.json()["access_token"])
        self.assertTrue(response.json()["refresh_token"])
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)

    def test_login_api_rejects_invalid_password(self):
        response = self.client.post(
            reverse("user_management_api:login_api"),
            data={
                "email": "login@example.com",
                "password": "wrong-password",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["ok"], False)
        self.assertEqual(response.json()["error"], "Invalid login credentials.")

    def test_login_api_rejects_inactive_user(self):
        inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password=self.password,
            is_active=False,
        )

        response = self.client.post(
            reverse("user_management_api:login_api"),
            data={
                "email": "inactive@example.com",
                "password": self.password,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["ok"], False)
        self.assertEqual(response.json()["error"], "Account is not active.")
        inactive_user.refresh_from_db()
        self.assertIsNone(inactive_user.last_login)

    def test_login_api_allows_phone_login(self):
        phone_user = User.objects.create_user(
            email=None,
            password=self.password,
            is_active=True,
            access_type="app",
            phone_number="+256781590905",
            phone_country_iso="UG",
        )

        response = self.client.post(
            reverse("user_management_api:login_api"),
            data={
                "phone_number": "0781590905",
                "phone_country_iso": "UG",
                "password": self.password,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ok"], True)
        self.assertEqual(
            set(response.json().keys()),
            {"ok", "access_token", "refresh_token"},
        )
        self.assertTrue(response.json()["access_token"])
        self.assertTrue(response.json()["refresh_token"])
        phone_user.refresh_from_db()
        self.assertIsNotNone(phone_user.last_login)

    def test_refresh_token_api_returns_new_tokens(self):
        login_response = self.client.post(
            reverse("user_management_api:login_api"),
            data={
                "email": "login@example.com",
                "password": self.password,
            },
        )

        refresh_response = self.client.post(
            reverse("user_management_api:refresh_token_api"),
            data={"refresh_token": login_response.json()["refresh_token"]},
        )

        self.assertEqual(refresh_response.status_code, 200)
        self.assertEqual(refresh_response.json()["ok"], True)
        self.assertIn("access_token", refresh_response.json())
        self.assertIn("refresh_token", refresh_response.json())
        self.assertEqual(refresh_response.json()["user_id"], self.user.id)

    def test_refresh_token_api_rejects_invalid_token(self):
        response = self.client.post(
            reverse("user_management_api:refresh_token_api"),
            data={"refresh_token": "not-a-real-token"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["ok"], False)
        self.assertEqual(response.json()["error"], "Invalid refresh token.")

    def test_set_password_OK(self):
        response = self.client.post(
            reverse("users:set_password", args=(self.pword_reset_token,)),
            {
                "new_password": "samplePword123",
                "confirm_password": "samplePword123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/email_sent.html")

    @patch("users.tasks.send_email_notification.delay")
    def test_request_password_reset_OK(self, mock_send_email):
        response = self.client.post(reverse("users:request_password_reset"), {"email": self.test_email})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/email_sent.html")

    def test_request_password_reset_wrong_email(self):
        response = self.client.post(reverse("users:request_password_reset"), {"email": "fake@email.com"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/request_password_reset.html")
        self.assertEqual(
            list(response.context["messages"])[0].message, _("requestPasswordResetViewErrorMessage")
        )

    def test_set_password_new_account_OK(self):
        invite_data = {
            "email": "test_invite@test.local",
            "role": "SCHEME",
            "scheme_id": Scheme.objects.first().id,
            "factory_id": Factory.objects.first().id,
        }
        invite = UserInvitations.objects.create(**invite_data)
        payload = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "invite_id": invite.id,
        }

        invite_token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.post(
            reverse("users:set_password", args=(invite_token,)),
            {
                "new_password": "samplePword123",
                "confirm_password": "samplePword123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/email_sent.html")

    def test_set_password_expired_token(self):
        payload = {
            "exp": datetime.now(tz=timezone.utc) - timedelta(days=1),
            "user_id": self.test_user.id,
        }
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.get(reverse("users:set_password", args=(token,)))
        self.assertEqual(response.status_code, 200)

    def test_set_password_invalid_token(self):
        payload = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "invalid_field": "invalid_value",
        }
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.get(reverse("users:set_password", args=(token,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/set_password.html")

    def test_set_password_account_not_found(self):
        payload = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "user_id": 9,
        }
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.post(
            reverse("users:set_password", args=(token,)),
            {"new_password": "samplePword123", "confirm_password": "samplePword123"},
        )
        self.assertEqual(response.status_code, 200)

    def test_set_password_form_validation(self):
        response = self.client.post(
            reverse("users:set_password", args=(self.pword_reset_token,)),
            {
                "new_password": "samplePword123",
                "confirm_password": "samplePword12",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            dict(response.context["form"].errors),
            {"confirm_password": [_("setPasswordFormErrorMessage")]},
        )

    def test_logout(self):
        response = self.client.get(reverse("users:logout_user"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("users:login_user"))

    def test_profile_page_renders_correctly(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")

    def test_change_email_page_renders_correctly(self):
        response = self.client.get(reverse("users:change_email"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/change_email.html")
        self.assertIsInstance(response.context["form"], ChangeEmailForm)

    @patch("users.tasks.send_email_notification.delay")
    def test_change_email_OK(self, mock_send_email):
        response = self.client.post(reverse("users:change_email"), {"new_email": "newEmail@test.local"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/email_sent.html")

    def test_change_email_to_old_email(self):
        response = self.client.post(reverse("users:change_email"), {"new_email": self.test_email})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/change_email.html")
        messages = [str(i) for i in response.context["messages"]]
        self.assertEqual(messages, ["New email must be different from current email!"])

    def test_change_email_to_existing_email(self):
        User.objects.create_user(email="test2@test.local", password=self.test_pword, is_active=True)
        response = self.client.post(reverse("users:change_email"), {"new_email": "test2@test.local"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/change_email.html")
        messages = [str(i) for i in response.context["messages"]]
        self.assertEqual(messages, ["A user with this email address already exists!"])

    def test_change_email_form_validation(self):
        response = self.client.post(reverse("users:change_email"), {"new_email": "email@testF"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/change_email.html")
        form_errors = dict(response.context["form"].errors)
        self.assertEqual(form_errors, {"new_email": ["Enter a valid email address."]})

    def test_verify_email_change_OK(self):
        payload = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "user_id": self.test_user.id,
            "new_email": "newEmail@test.local",
        }
        change_email_token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.get(reverse("users:verify_email", args=(change_email_token,)))
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(id=self.test_user.id)
        self.assertEqual(user.email, "newEmail@test.local")

    def test_verify_email_change_invalid_token(self):
        payload = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "invalid_field": "invalid_value",
        }
        change_email_token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.get(reverse("users:verify_email", args=(change_email_token,)))
        self.assertEqual(response.status_code, 302)

    def test_verify_email_change_expired_token(self):
        payload = {
            "exp": datetime.now(tz=timezone.utc) - timedelta(days=1),
            "user_id": self.test_user.id,
            "new_email": "newEmail@test.local",
        }
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.get(reverse("users:verify_email", args=(token,)))
        self.assertEqual(response.status_code, 302)
