import jwt
from django.conf import settings
from rest_framework import authentication, exceptions

from users.models import User


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode("utf-8")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token = parts[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError as exc:
            raise exceptions.AuthenticationFailed("Access token has expired.") from exc
        except jwt.InvalidTokenError as exc:
            raise exceptions.AuthenticationFailed("Invalid access token.") from exc

        if payload.get("token_type") != "access":
            raise exceptions.AuthenticationFailed("Invalid access token.")

        user = User.objects.filter(id=payload.get("user_id")).first()
        if not user:
            raise exceptions.AuthenticationFailed("User not found.")
        if not user.is_active:
            raise exceptions.AuthenticationFailed("User account is inactive.")

        return user, token

    def authenticate_header(self, request):
        return self.keyword
