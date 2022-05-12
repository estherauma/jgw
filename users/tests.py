import email
import imp

from django.forms.utils import ErrorDict
from django.test import TestCase
from django.urls import reverse

from .models import User


class AuthTests(TestCase):
    def setUp(self) -> None:
        self.test_email = "test@test.local"
        self.test_pword = "12t32thome"
        user = User.objects.create_user(self.test_email, self.test_pword)
        self.test_user = user
        self.client.force_login(user=self.test_user)

    def test_authorisation(self):
        """
        Test dashboard views require email/pword login to access
        """
        response = self.client.get(reverse("dashboard:preferences"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/")
        response = self.client.get(reverse("dashboard:inline"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/inline-questions")

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
        self.assertTrue(isinstance(response.context["form"].errors, ErrorDict))
