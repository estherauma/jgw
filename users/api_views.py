from django.db import transaction
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.api_serializers import (
    ErrorResponseSerializer,
    FormErrorResponseSerializer,
    LoginRequestSerializer,
    LoginResponseSerializer,
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
                "user_id": user.id,
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
