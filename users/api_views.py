from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.forms import APIAppUserForm, APIDashboardUserForm
from users.services.authentication import (
    create_registration_verification_code,
    login_api_user,
    refresh_api_access_token,
    resend_registration_verification_code,
    send_registration_verification_email,
    send_registration_verification_sms,
    verify_registration_code,
)
from users.views import initialize_user_dashboard_preferences
from user_management.services.user import (
    assign_default_app_registration_membership,
)


class RegisterUserApiView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            access_type = (
                "dashboard"
                if (request.data.get("access_type") or "").strip().lower() == "dashboard"
                else "app"
            )

            form_class = APIDashboardUserForm if access_type == "dashboard" else APIAppUserForm
            form = form_class(data=request.data)
            if not form.is_valid():
                return Response(
                    {"ok": False, "errors": form.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                user = form.save(commit=False)
                user.is_active = False
                user.access_type = access_type
                user.set_password(form.cleaned_data["password1"])
                user.save()
                if access_type == "app":
                    assign_default_app_registration_membership(
                        user,
                        form.cleaned_data["organisation"],
                    )
                else:
                    initialize_user_dashboard_preferences(user, request)
                _, verification_code = create_registration_verification_code(user)

            if user.email:
                send_registration_verification_email(user, verification_code)
            else:
                sms_sent = send_registration_verification_sms(user, verification_code)
                if not sms_sent:
                    return Response(
                        {
                            "ok": False,
                            "error": "User was registered, but the verification SMS could not be sent.",
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
        except Exception as e:
            return Response(
                {
                    "ok": False,
                    "error": "Could not register user. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            {
                "ok": True,
                "user_id": user.id,
                "email": user.email,
                "phone_number": user.phone_number,
                "phone_country_iso": user.phone_country_iso,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginApiView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            result = login_api_user(
                email=request.data.get("email"),
                phone_number=request.data.get("phone_number"),
                phone_country_iso=request.data.get("phone_country_iso"),
                password=request.data.get("password"),
            )
        except Exception:
            return Response(
                {
                    "ok": False,
                    "error": "Could not log in. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not result["ok"]:
            return Response(
                {"ok": False, "error": result["error"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tokens = result["tokens"]
        return Response(
            {
                "ok": True,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                
            },
            status=status.HTTP_200_OK,
        )


class RefreshTokenApiView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            result = refresh_api_access_token(
                request.data.get("refresh_token"),
            )
        except Exception:
            return Response(
                {
                    "ok": False,
                    "error": "Could not refresh the access token. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not result["ok"]:
            return Response(
                {"ok": False, "error": result["error"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = result["user"]
        tokens = result["tokens"]
        return Response(
            {
                "ok": True,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "user_id": user.id,
            },
            status=status.HTTP_200_OK,
        )


class VerifyRegistrationCodeApiView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            result = verify_registration_code(
                code=request.data.get("code"),
                email=request.data.get("email"),
                phone_number=request.data.get("phone_number"),
                phone_country_iso=request.data.get("phone_country_iso"),
            )
        except Exception:
            return Response(
                {
                    "ok": False,
                    "error": "Could not verify registration code. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        if not result["ok"]:
            return Response(
                {"ok": False, "error": result["error"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"ok": True, "user_id": result["user"].id},
            status=status.HTTP_200_OK,
        )


class ResendRegistrationCodeApiView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            result = resend_registration_verification_code(
                user_id=request.data.get("user_id"),
                email=request.data.get("email"),
                phone_number=request.data.get("phone_number"),
                phone_country_iso=request.data.get("phone_country_iso"),
            )
        except Exception:
            return Response(
                {
                    "ok": False,
                    "error": "Could not resend the verification code. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not result["ok"]:
            return Response(
                {"ok": False, "error": result["error"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = result["user"]
        return Response(
            {
                "ok": True,
                "user_id": user.id,
                "email": user.email,
                "phone_number": user.phone_number,
                "phone_country_iso": user.phone_country_iso,
            },
            status=status.HTTP_200_OK,
        )
