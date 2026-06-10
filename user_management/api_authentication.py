from dataclasses import dataclass

from django.conf import settings
from rest_framework import authentication, exceptions


@dataclass
class ExternalApiPrincipal:
    name: str = "external_api"

    @property
    def is_authenticated(self):
        return True


class ExternalApiKeyAuthentication(authentication.BaseAuthentication):
    header_name = "HTTP_X_API_KEY"

    def authenticate(self, request):
        configured_key = (getattr(settings, "EXTERNAL_API_KEY", "") or "").strip()
        if not configured_key:
            raise exceptions.AuthenticationFailed("External API authentication is not configured.")

        provided_key = (request.META.get(self.header_name, "") or "").strip()
        if not provided_key:
            raise exceptions.AuthenticationFailed("API key was not provided.")

        if provided_key != configured_key:
            raise exceptions.AuthenticationFailed("Invalid API key.")

        return ExternalApiPrincipal(), provided_key

    def authenticate_header(self, request):
        return "X-API-Key"
