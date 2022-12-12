import email
import imp

from django.forms.utils import ErrorDict
from django.test import TestCase
from django.urls import reverse

from .forms import CreateUserForm, InviteUserForm, UserMgtForm
from .models import User


class AuthTests(TestCase):
    def setUp(self) -> None:
        super(AuthTests, self).setUp()
        self.test_email = "test@test.local"
        self.test_pword = "12t32thome"
        user = User.objects.create_user(email=self.test_email, password=self.test_pword, is_active=True)
        self.test_user = user
        self.client.login(email=self.test_user, password=self.test_pword)

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

    def test_account_creation_and_login(self):
        """
        Test sign up and login, form validation
        """
        # test create user and login user
        response = self.client.post(
            reverse("users:create_user"),
            {"email": "test2@test.local", "password1": self.test_pword, "password2": self.test_pword},
        )
        # redirects to login if signup ok.
        self.assertRedirects(response, reverse("users:login_user"))
        response = self.client.post(
            reverse("users:login_user"), {"email": "test2@test.local", "password1": self.test_pword}
        )
        self.assertEqual(response.status_code, 200)
        # test form validation and errors
        response = self.client.post(
            reverse("users:create_user"),
            {"email": "test2@test.local", "password1": self.test_pword, "password2": ""},
        )
        self.assertIsNotNone(response.context["form"].errors)
        self.assertIsInstance(response.context["form"].errors, ErrorDict)

    def test_invite_user_view_renders_correctly(self):
        response = self.client.get(reverse("users:invite_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/invite_user.html")
        self.assertIsInstance(response.context["form"], InviteUserForm)

    def test_manage_user_view_renders_correctly(self):
        response = self.client.get(reverse("users:manage_user", args=(self.test_user.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/manage_user.html")
        self.assertIsInstance(response.context["form"], UserMgtForm)

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