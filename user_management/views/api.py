import logging

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from user_management.api_authentication import ExternalApiKeyAuthentication
from user_management.api_serializers import (
    AccessCodeLookupErrorSerializer,
    AccessCodeLookupResponseSerializer,
    AccessCodeStatusResponseSerializer,
    AuthenticationErrorDetailSerializer,
    PartnerConfigOrganizationSerializer,
)
from user_management.services.organization import OrganizationService


logger = logging.getLogger(__name__)


class AccessCodeStatusApiView(APIView):
    authentication_classes = []

    @extend_schema(
        tags=["User Management"],
        summary="Get access code status",
        description="Looks up an organisation access code and returns whether it requires login.",
        responses={
            200: AccessCodeStatusResponseSerializer,
            404: AccessCodeLookupErrorSerializer,
        },
        examples=[
            OpenApiExample(
                "Access code status response",
                value={
                    "code": "TEST123",
                    "requires_login": True,
                },
                response_only=True,
            )
        ],
    )
    def get(self, request, access_code):
        try:
            result = OrganizationService.get_access_code_status(access_code=access_code)
            if not result:
                return Response(
                    {"ok": False, "error": "Access code not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(result, status=status.HTTP_200_OK)
        except Exception:
            logger.exception(
                "Failed to fetch access code status.",
                extra={"access_code": access_code},
            )
            return Response(
                {"ok": False, "error": "Could not fetch access code status. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AccessCodeDetailsApiView(APIView):
    @extend_schema(
        tags=["User Management"],
        summary="Get access code details",
        description=(
            "Looks up an organisation access code and returns the access code details, "
            "the linked organisation, and the attached work groups. Public access codes can "
            "be fetched without authentication. Access codes that require login still require "
            "an authenticated user from the same organisation."
        ),
        responses={
            200: AccessCodeLookupResponseSerializer,
            401: AccessCodeLookupErrorSerializer,
            403: AccessCodeLookupErrorSerializer,
            404: AccessCodeLookupErrorSerializer,
        },
        examples=[
            OpenApiExample(
                "Access code lookup response",
                value={
                    "id": 12,
                    "code": "TEST123",
                    "requires_login": False,
                    "expiry_date": None,
                    "organization": {
                        "id": 5,
                        "name": "Test Org",
                        "org_code": "TESTORG",
                        "display_name": "Test Organisation",
                        "has_custom_content": True,
                        "theme": "default",
                        "custom_type": "version_1",
                        "work_sector": "Agriculture",
                        "content_collection": "test-org",
                        "default_collection_language": "en",
                        "default_feedback_emails": "feedback@example.com",
                        "default_report_issue_emails": "report@example.com",
                        "collection_languages": [
                            {"code": "en", "name": "English"},
                            {"code": "sw", "name": "Swahili"},
                        ],
                        "big_icon_url": "https://cdn.example.com/big.png",
                        "small_icon_url": "https://cdn.example.com/small.png",
                    },
                    "access_code_user_groups": [
                        {"id": 3, "name": "Worker"},
                        {"id": 4, "name": "Supervisor"},
                    ],
                },
                response_only=True,
            )
        ],
    )
    def get(self, request, access_code):
        try:
            result = OrganizationService.get_access_code_details(
                access_code=access_code,
                user=request.user,
            )
            if not result:
                return Response(
                    {"ok": False, "error": "Access code not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not result.get("requires_login"):
                return Response(result, status=status.HTTP_200_OK)

            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication credentials were not provided."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            organization = result.get("organization")
            has_membership = request.user.organisation_data.filter(id=organization["id"]).exists()
            if not has_membership:
                return Response(
                    {"ok": False, "error": "You do not have access to this organisation."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return Response(
                result,
                status=status.HTTP_200_OK,
            )
        except Exception:
            logger.exception(
                "Failed to fetch access code details.",
                extra={"access_code": access_code, "user_id": request.user.id},
            )
            return Response(
                {"ok": False, "error": "Could not fetch access code details. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PartnerConfigsApiView(APIView):
    authentication_classes = [ExternalApiKeyAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["User Management"],
        summary="Get partner config",
        description=(
            "Returns the full partner configuration payload for all organisations. "
            "This endpoint is protected by the external API key."
        ),
        responses={
            200: PartnerConfigOrganizationSerializer(many=True),
            401: AuthenticationErrorDetailSerializer,
        },
        examples=[
            OpenApiExample(
                "Partner config lookup response",
                value=[
                    {
                        "id": 5,
                        "name": "Test Org",
                        "org_code": "TESTORG",
                        "display_name": "Test Organisation",
                        "has_custom_content": True,
                        "theme": "default",
                        "custom_type": "version_1",
                        "work_sector": "Agriculture",
                        "content_collection": "test-org",
                        "default_collection_language": "en",
                        "default_feedback_emails": "feedback@example.com",
                        "default_report_issue_emails": "report@example.com",
                        "cms_id": None,
                        "cms_sync_status": "pending",
                        "last_cms_sync_date": None,
                        "collection_languages": [
                            {"code": "en", "name": "English"},
                            {"code": "sw", "name": "Swahili"},
                        ],
                        "access_codes": [
                            {
                                "id": 12,
                                "code": "TEST123",
                                "requires_login": True,
                                "expiry_date": None,
                            }
                        ],
                        "user_groups": [
                            {"id": 3, "name": "Worker"},
                            {"id": 4, "name": "Supervisor"},
                        ],
                        "big_icon_url": "https://cdn.example.com/big.png",
                        "small_icon_url": "https://cdn.example.com/small.png",
                    }
                ],
                response_only=True,
            )
        ],
    )
    def get(self, request):
        try:
            result = OrganizationService.get_partner_configs()
            return Response(result, status=status.HTTP_200_OK)
        except Exception:
            logger.exception(
                "Failed to fetch partner config.",
            )
            return Response(
                {
                    "ok": False,
                    "error": "Could not fetch partner config. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
