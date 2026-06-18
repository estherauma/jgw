import base64
import io
import json
import segno
import requests
from django.conf import settings
from django.utils.text import slugify


class BranchService:
    endpoint = "https://api2.branch.io/v1/url"

    @classmethod
    def get_work_code_payload(cls, *, work_code):
        branch_key = getattr(settings, "BRANCH_KEY", "").strip()
        branch_link_domain = getattr(settings, "BRANCH_LINK_DOMAIN", "").strip()

        if not branch_key:
            raise ValueError("BRANCH_KEY is not configured.")
        if not branch_link_domain:
            raise ValueError("BRANCH_LINK_DOMAIN is not configured.")

        return {
            "branch_key": branch_key,
            "domain": branch_link_domain,
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

    @classmethod
    def get_or_create_work_code_deep_link(cls, *, work_code):
        branch_url = (work_code.deep_link or "").strip()

        if not branch_url:
            payload = cls.get_work_code_payload(work_code=work_code)

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
                raise ValueError(
                    response.text or f"Branch returned HTTP {response.status_code}."
                )

            branch_url = response_data.get("url")
            if not branch_url:
                raise ValueError("Branch did not return a generated URL.")

            work_code.deep_link = branch_url
            work_code.save(update_fields=["deep_link", "updated_at"])
        return branch_url

    @classmethod
    def create_qr_code_url(cls, *, deep_link):
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

    @classmethod
    def create_work_code_deep_link(cls, *, work_code):
        branch_url = cls.get_or_create_work_code_deep_link(work_code=work_code)
        return {
            "url": branch_url,
            "qr_code_url": cls.create_qr_code_url(deep_link=branch_url),
        }
