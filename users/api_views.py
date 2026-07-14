from django.db import transaction
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.api_serializers import (
    CurrentUserResponseSerializer,
    ErrorResponseSerializer,
    FormErrorResponseSerializer,
    LoginRequestSerializer,
    LoginResponseSerializer,
    PasswordResetRequestResponseSerializer,
    PasswordResetRequestSerializer,
    PasswordResetResetRequestSerializer,
    PasswordResetResetResponseSerializer,
    PasswordResetTokenResetRequestSerializer,
    PasswordResetTokenResetResponseSerializer,
    PasswordResetVerifyCodeRequestSerializer,
    PasswordResetVerifyCodeResponseSerializer,
    RefreshTokenRequestSerializer,
    RefreshTokenResponseSerializer,
    RegisterUserRequestSerializer,
    RegisterUserResponseSerializer,
    ResendRegistrationCodeRequestSerializer,
    ResendRegistrationCodeResponseSerializer,
    VerifyRegistrationCodeRequestSerializer,
    VerifyRegistrationCodeResponseSerializer,
)
from users.forms import APIAppUserForm, APIDashboardUserForm
from users.services.authentication import (
    REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
    create_user_verification_code,
    login_api_user,
    request_password_reset_code,
    reset_password_with_code,
    reset_password_with_token,
    refresh_api_access_token,
    resend_registration_verification_code,
    send_code_email,
    send_code_sms,
    verify_password_reset_code,
    verify_registration_code,
)
from users.services.profile import get_current_user_payload
from users.views import initialize_user_dashboard_preferences
from user_management.services.user import (
    assign_default_app_registration_membership,
)


class CurrentUserApiView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Authentication"],
        summary="Get current user",
        description="Returns the currently authenticated user linked to the access token.",
        responses={
            200: CurrentUserResponseSerializer,
            401: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                "Current user response",
                value={
                    "id": 123,
                    "email": "john.doe@example.com",
                    "phone_number": None,
                    "phone_country_iso": None,
                    "first_name": "John",
                    "last_name": "Doe",
                    "role": "worker",
                    "access_type": "dashboard",
                    "is_active": True,
                    "organisation": {
                        "id": 5,
                        "name": "Test Org",
                        "org_code": "TESTORG",
                        "display_name": "Test Organisation",
                        "user_groups": [
                            {
                                "id": 3,
                                "name": "Worker",
                            }
                        ],
                        "access_codes": [
                            {
                                "id": 11,
                                "code": "PUBLIC123",
                                "requires_login": False,
                                "expiry_date": None,
                            },
                            {
                                "id": 12,
                                "code": "PRIVATE123",
                                "requires_login": True,
                                "expiry_date": None,
                            },
                        ],
                    },
                },
                response_only=True,
            )
        ],
    )
    def get(self, request):
        return Response(get_current_user_payload(request.user), status=status.HTTP_200_OK)


class RegisterUserApiView(APIView):
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Register a new user",
        description=(
            "Creates an inactive app or dashboard user, then sends a verification code by email "
            "or SMS depending on the contact details provided."
        ),
        request=RegisterUserRequestSerializer,
        responses={
            201: RegisterUserResponseSerializer,
            400: FormErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                "App registration with email",
                value={
                    "access_type": "app",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "password1": "StrongPassword123!",
                    "org_code": "TESTORG",
                },
                request_only=True,
            ),
            OpenApiExample(
                "App registration with phone",
                value={
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone_number": "0700000000",
                    "phone_country_iso": "UG",
                    "password1": "StrongPassword123!",
                    "org_code": "TESTORG",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Dashboard registration",
                value={
                    "access_type": "dashboard",
                    "first_name": "Jane",
                    "last_name": "Admin",
                    "email": "jane.admin@example.com",
                    "password1": "StrongPassword123!",
                },
                request_only=True,
            ),
        ],
    )
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
                _, verification_code = create_user_verification_code(
                    user,
                    REGISTRATION_EMAIL_VERIFICATION_PURPOSE,
                )

            if user.email:
                send_code_email(
                    user,
                    verification_code,
                    "users/registration-verification-email.html",
                    "Verify your email - Just Good Work",
                )
            else:
                sms_sent = send_code_sms(
                    user,
                    f"Your Just Good Work verification code is {verification_code}. "
                    f"It expires in 15 minutes.",
                )
                if not sms_sent:
                    return Response(
                        {
                            "ok": False,
                            "error": "User was registered, but the verification SMS could not be sent.",
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
        except Exception:
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
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Log in",
        description="Authenticates a user with email or phone number and returns JWT tokens.",
        request=LoginRequestSerializer,
        responses={
            200: LoginResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                "Login with email",
                value={
                    "email": "login@example.com",
                    "password": "StrongPassword123!",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Login with phone",
                value={
                    "phone_number": "0700000000",
                    "phone_country_iso": "UG",
                    "password": "StrongPassword123!",
                },
                request_only=True,
            ),
        ],
    )
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

        if result.get("has_expired_temporary_password"):
            return Response(
                {
                    "ok": True,
                    "has_expired_temporary_password": True,
                },
                status=status.HTTP_200_OK,
            )

        if result.get("requires_password_reset"):
            return Response(
                {
                    "ok": True,
                    "requires_password_reset": True,
                    "password_reset_token": result["password_reset_token"],
                },
                status=status.HTTP_200_OK,
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
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Refresh access token",
        request=RefreshTokenRequestSerializer,
        responses={
            200: RefreshTokenResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                "Refresh token request",
                value={"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
                request_only=True,
            )
        ],
    )
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
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestApiView(APIView):
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Request password reset code",
        description="Sends a password reset verification code to the user's email or phone number.",
        request=PasswordResetRequestSerializer,
        responses={
            200: PasswordResetRequestResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                "Request reset with email",
                value={"email": "login@example.com"},
                request_only=True,
            ),
            OpenApiExample(
                "Request reset with phone",
                value={
                    "phone_number": "0700000000",
                    "phone_country_iso": "UG",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")
        phone_country_iso = request.data.get("phone_country_iso")
        try:
            result = request_password_reset_code(
                email=email,
                phone_number=phone_number,
                phone_country_iso=phone_country_iso,
            )
        except Exception:
            return Response(
                {
                    "ok": False,
                    "error": "Could not request a password reset code. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not result["ok"]:
            return Response(
                {"ok": False, "error": result["error"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "ok": True,
                "email": email or None,
                "phone_number": phone_number or None,
                "phone_country_iso": phone_country_iso or None,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetVerifyCodeApiView(APIView):
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Verify password reset code",
        description="Verifies a password reset code for the provided email or phone number.",
        request=PasswordResetVerifyCodeRequestSerializer,
        responses={
            200: PasswordResetVerifyCodeResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                "Verify reset code with email",
                value={
                    "email": "login@example.com",
                    "code": "AXRDP5",
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        try:
            result = verify_password_reset_code(
                code=request.data.get("code"),
                email=request.data.get("email"),
                phone_number=request.data.get("phone_number"),
                phone_country_iso=request.data.get("phone_country_iso"),
            )
        except Exception:
            return Response(
                {
                    "ok": False,
                    "error": "Could not verify the password reset code. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not result["ok"]:
            return Response(
                {"ok": False, "error": result["error"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "ok": True,
                "user_id": result["user"].id,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetResendApiView(APIView):
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Resend password reset code",
        description="Sends a fresh password reset verification code to the user's email or phone number.",
        request=PasswordResetRequestSerializer,
        responses={
            200: PasswordResetRequestResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")
        phone_country_iso = request.data.get("phone_country_iso")
        try:
            result = request_password_reset_code(
                email=email,
                phone_number=phone_number,
                phone_country_iso=phone_country_iso,
            )
        except Exception:
            return Response(
                {
                    "ok": False,
                    "error": "Could not resend the password reset code. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not result["ok"]:
            return Response(
                {"ok": False, "error": result["error"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "ok": True,
                "email": email or None,
                "phone_number": phone_number or None,
                "phone_country_iso": phone_country_iso or None,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetResetApiView(APIView):
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Reset password",
        description="Resets the user's password using the verified reset code.",
        request=PasswordResetResetRequestSerializer,
        responses={
            200: PasswordResetResetResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        try:
            result = reset_password_with_code(
                code=request.data.get("code"),
                password=request.data.get("password"),
                email=request.data.get("email"),
                phone_number=request.data.get("phone_number"),
                phone_country_iso=request.data.get("phone_country_iso"),
            )
        except Exception:
            return Response(
                {
                    "ok": False,
                    "error": "Could not reset the password. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not result["ok"]:
            return Response(
                {"ok": False, "error": result["error"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"ok": True, "user_id": result["user"].id}, status=status.HTTP_200_OK)


class PasswordResetTokenResetApiView(APIView):
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Reset temporary password",
        description=(
            "Resets the password for users who signed in with a one-time temporary password, "
            "then returns normal API tokens."
        ),
        request=PasswordResetTokenResetRequestSerializer,
        responses={
            200: PasswordResetTokenResetResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        try:
            result = reset_password_with_token(
                password_reset_token=request.data.get("password_reset_token"),
                password=request.data.get("password"),
            )
        except Exception:
            return Response(
                {
                    "ok": False,
                    "error": "Could not reset the password. Please try again.",
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


class VerifyRegistrationCodeApiView(APIView):
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Verify registration code",
        description="Verifies the code sent during registration and activates the user account.",
        request=VerifyRegistrationCodeRequestSerializer,
        responses={
            200: VerifyRegistrationCodeResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                "Verify with email",
                value={
                    "email": "john.doe@example.com",
                    "code": "AXRDP5",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Verify with phone",
                value={
                    "phone_number": "0700000000",
                    "phone_country_iso": "UG",
                    "code": "AXRDP5",
                },
                request_only=True,
            ),
        ],
    )
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
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Resend registration code",
        description="Sends a fresh registration verification code to the user's email or phone.",
        request=ResendRegistrationCodeRequestSerializer,
        responses={
            200: ResendRegistrationCodeResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                "Resend with email",
                value={"email": "john.doe@example.com"},
                request_only=True,
            ),
            OpenApiExample(
                "Resend with phone",
                value={
                    "phone_number": "0700000000",
                    "phone_country_iso": "UG",
                },
                request_only=True,
            ),
        ],
    )
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
