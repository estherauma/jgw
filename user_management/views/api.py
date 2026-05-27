import logging

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user_management.api_serializers import (
    AccessCodeLookupErrorSerializer,
    AccessCodeLookupResponseSerializer,
)
from user_management.services.organization import OrganizationService


logger = logging.getLogger(__name__)


class AccessCodeDetailsApiView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["User Management"],
        summary="Get access code details",
        description=(
            "Looks up an organisation access code and returns the access code details, "
            "the linked organisation, and the attached work groups."
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
                        "display_name": "Test Org",
                        "theme": "default",
                        "work_sector": "Agriculture",
                        "content_collection": "test-org",
                        "default_collection_language": "en",
                    },
                    "workgroups": [
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
            result = OrganizationService.get_access_code_details(access_code=access_code)
            if not result:
                return Response(
                    {"ok": False, "error": "Access code not found."},
                    status=status.HTTP_404_NOT_FOUND,
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
