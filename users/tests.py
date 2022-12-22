from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from dashboard.models import Factory, Scheme

from .forms import CreateUserForm, InviteUserForm, SetPasswordForm, UserMgtForm
from .models import User, UserInvitations


class AuthTests(TestCase):
    def setUp(self) -> None:
        super(AuthTests, self).setUp()
        self.test_email = "test@test.local"
        self.test_pword = "12t32thome"
        self.test_user = User.objects.create_user(
            email=self.test_email, password=self.test_pword, is_active=True
        )
        self.client.login(email=self.test_user, password=self.test_pword)
        self.test_scheme = Scheme.objects.create(name="Test_Scheme")
        self.test_factory = Factory.objects.create(name="Test_Factory")
        payload = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "user_id": self.test_user.id,
        }
        self.pword_reset_token = jwt.encode(payload=payload, key=settings.SECRET_KEY)

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
        self.assertRedirects(response, "/accounts/login/?next=/")

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
        self.assertRedirects(response, reverse("dashboard:inline"))

    def test_login_form_validation(self):
        """
        Test login form validation
        """
        response = self.client.post(
            reverse("users:login_user"), {"email": "test2@test.local", "password": self.test_pword}
        )
        messages = [str(i) for i in response.context["messages"]]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(messages, ["Can not log in with provided credentials!"])
        response = self.client.post(
            reverse("users:login_user"), {"email": "test@fakeemail.", "password": self.test_pword}
        )
        form_errors = dict(response.context["form"].errors)
        self.assertEqual(form_errors, {"email": ["Enter a valid email address."]})

    def test_invite_user_view_renders_correctly(self):
        response = self.client.get(reverse("users:invite_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/invite_user.html")
        self.assertIsInstance(response.context["form"], InviteUserForm)

    def test_invite_user_OK(self):
        response = self.client.post(
            reverse("users:invite_user"),
            {
                "email": "test_invite@test.local",
                "role": "SCHEME",
                "scheme": Scheme.objects.first().id,
                "factory": Factory.objects.first().id,
                "organisation": "Seasonal Worker Scheme - AG Recruitment",
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
                "organisation": "Seasonal Worker Scheme - AG Recruitment",
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

    def test_activate_user_OK(self):
        new_user = User.objects.create_user(email="test2@test.local", password=self.test_pword)
        response = self.client.get(reverse("users:activate_account", args=(new_user.id,)))
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(email="test2@test.local")
        self.assertTrue(new_user.is_active)
        self.assertRedirects(response, "/accounts/")
    
    def test_create_user_view_renders_correctly(self):
        response = self.client.get(reverse("users:create_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/create_user.html")
        self.assertIsInstance(response.context["form"], CreateUserForm)

    def test_list_users_view_renders_correctly(self):
        response = self.client.get(reverse("users:list_users"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/list_users.html")
        self.assertEqual(len(response.context["users"]), 1)
        self.assertEqual(response.context["users"][0], self.test_user)

    def test_handle_invite_view_OK(self):
        invite_data = {
            "email": "test_invite@test.local",
            "role": "SCHEME",
            "scheme_id": Scheme.objects.first().id,
            "factory_id": Factory.objects.first().id,
            "organisation": "Seasonal Worker Scheme - AG Recruitment",
        }
        invite = UserInvitations.objects.create(**invite_data)
        payload = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "invite_id": invite.id,
        }
        invite_token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.get(reverse("users:handle_invite", args=(invite_token,)))
        self.assertEqual(response.status_code, 302)
        invite = UserInvitations.objects.first()
        self.assertEqual(invite.status, "ACCEPTED")

    def test_handle_invite_view_expired_token(self):
        invite_data = {
            "email": "test_invite@test.local",
            "role": "SCHEME",
            "scheme_id": Scheme.objects.first().id,
            "factory_id": Factory.objects.first().id,
            "organisation": "Seasonal Worker Scheme - AG Recruitment",
        }
        invite = UserInvitations.objects.create(**invite_data)
        payload = {
            "exp": datetime.now(tz=timezone.utc) - timedelta(days=1),
            "invite_id": invite.id,
        }
        invite_token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.get(reverse("users:handle_invite", args=(invite_token,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["messages"])[0].message, "This link is expired!")

    def test_handle_invite_view_invalid_invitation(self):
        payload = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "invite_id": 3,
        }
        invite_token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.get(reverse("users:handle_invite", args=(invite_token,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["messages"])[0].message, "Invitation not found!")

    def test_set_password_view_renders_correctly(self):
        response = self.client.get(reverse("users:set_password", args=(self.pword_reset_token,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/set_password.html")
        self.assertIsInstance(response.context["form"], SetPasswordForm)

    def test_set_password_OK(self):
        response = self.client.post(
            reverse("users:set_password", args=(self.pword_reset_token,)),
            {
                "new_password": "samplePword123",
                "confirm_password": "samplePword123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/")

    def test_set_password_new_account_OK(self):
        invite_data = {
            "email": "test_invite@test.local",
            "role": "SCHEME",
            "scheme_id": Scheme.objects.first().id,
            "factory_id": Factory.objects.first().id,
            "organisation": "Seasonal Worker Scheme - AG Recruitment",
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
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/")

    def test_set_password_expired_token(self):
        payload = {
            "exp": datetime.now(tz=timezone.utc) - timedelta(days=1),
            "user_id": self.test_user.id,
        }
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        response = self.client.get(reverse("users:set_password", args=(token,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["messages"])[0].message, "This link is expired!")

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
        self.assertEqual(list(response.context["messages"])[0].message, "User account not found!")

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
            {"confirm_password": ["The two password fields didn’t match."]},
        )

    def test_logout(self):
        response = self.client.get(reverse("users:logout_user"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("users:login_user"))
