import email
import imp

from django.forms.utils import ErrorDict
from django.test import TestCase
from django.urls import reverse

from .models import User


class AuthTests(TestCase):
    def setUp(self) -> None:
        self.test_email = "test@test.local"
        self.test_password = "12t32thome"
        user = User.objects.create_user(self.test_email, self.test_password)
        self.test_user = user
        self.client.force_login(user=self.test_user)

    def test_authorisation(self):
        """
        Test dashboard views require email/pword login to access
        """
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_account_creation(self):
        """
        Test account creation and sign up form validation
        """
        response = self.client.post(
            reverse("users:create_user"),
            {"email": "test2@test.local", "password1": self.test_password, "password2": self.test_password},
        )
        self.assertRedirects(response, reverse("users:login_user"))
        response = self.client.post(
            reverse("users:create_user"),
            {"email": "test2@test.local", "password1": self.test_password, "password2": ""},
        )
        self.assertIsNotNone(response.context["form"].errors)
        self.assertTrue(isinstance(response.context["form"].errors, ErrorDict))
