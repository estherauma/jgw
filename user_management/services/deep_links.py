import base64
import io
import json
import segno
import requests
from django.conf import settings
from django.utils.text import slugify


class DeepLinkService:
    endpoint = "https://api2.branch.io/v1/url"

    @staticmethod
    def get_conflicting_branch_url(*, response_data):
        error_data = response_data.get("error")
        if not isinstance(error_data, dict):
            return None

        message = (error_data.get("message") or "").strip()
        conflict_prefix = "Link alias conflict:"
        if not message.startswith(conflict_prefix):
            return None

        conflict_url = message[len(conflict_prefix) :].strip()
        return conflict_url or None

    @classmethod
    def create_branch_deep_link(cls, *, payload):
        branch_key = getattr(settings, "BRANCH_KEY", "").strip()
        branch_link_domain = getattr(settings, "BRANCH_LINK_DOMAIN", "").strip()

        if not branch_key:
            raise ValueError("BRANCH_KEY is not configured.")
        if not branch_link_domain:
            raise ValueError("BRANCH_LINK_DOMAIN is not configured.")

        payload = {
            "branch_key": branch_key,
            "domain": branch_link_domain,
            **payload,
        }
        try:
            response = requests.post(
                cls.endpoint,
                json=payload,
                timeout=30,
            )
            response_data = response.json()
        except requests.RequestException as exc:
            raise ValueError(f"Could not reach Branch: {exc}") from exc

        if not response.ok:
            conflicting_branch_url = cls.get_conflicting_branch_url(
                response_data=response_data
            )
            if conflicting_branch_url:
                return conflicting_branch_url
            raise ValueError(
                response.text or f"Branch returned HTTP {response.status_code}."
            )

        branch_url = response_data.get("url")
        if not branch_url:
            raise ValueError("Branch did not return a generated URL.")

        return branch_url

    @classmethod
    def get_or_create_login__deep_link(cls, *, work_code):
        branch_url = (work_code.deep_link or "").strip()

        if not branch_url:
            payload = {
                "alias": f"{slugify(work_code.organisation.name)}-{work_code.id}",
                "feature": "login",
                "campaign": "user_management",
                "tags": [work_code.organisation.name],
                "data": {
                    "$marketing_title": f"{work_code.organisation.name} - Login ",
                    "type": "login",
                    "organisationAccessCode": work_code.code,
                },
            }
            branch_url = cls.create_branch_deep_link(payload=payload)
            work_code.deep_link = branch_url
            work_code.save(update_fields=["deep_link", "updated_at"])
        return {
            "url": branch_url,
            "qr_code_url": cls.create_qr_code(deep_link=branch_url),
        }

    @classmethod
    def create_qr_code(cls, *, deep_link):
        qr_code = segno.make(deep_link)
        qr_buffer = io.BytesIO()
        qr_code.save(
            qr_buffer,
            kind="svg",
            scale=8,
            dark="#193560",
            light="#FFFFFF",
            border=1,
        )
        return "data:image/svg+xml;base64,{image}".format(
            image=base64.b64encode(qr_buffer.getvalue()).decode("ascii"),
        )
