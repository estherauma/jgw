from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db.models import Exists, OuterRef

from content.services.partner_configurations import FileUploadError, upload_files_to_cms
from preference.models import (
    OrganizationGroup,
    OrganisationAccessCode,
    OrganisationData,
    SiteLanguages,
)
from user_management.permissions import is_flag_active
from user_management.utils import is_org_admin_or_staff, is_super_or_58_admin


class OrganizationService:
    @staticmethod
    def get_allowed_orgs(user):
        if user.is_anonymous:
            return OrganisationData.objects.none()
        if is_super_or_58_admin(user):
            return OrganisationData.objects.all()
        if is_org_admin_or_staff(user):
            org = user.organisation_data.order_by("name").first()
            if not org:
                return OrganisationData.objects.none()
            return OrganisationData.objects.filter(id=org.id)
        return OrganisationData.objects.none()

    @staticmethod
    def has_org_access(user, organisation, request=None, flag_name=None):
        if not organisation:
            return False
        if not OrganizationService.get_allowed_orgs(user).filter(
            id=organisation.id
        ).exists():
            return False
        if flag_name and request and is_org_admin_or_staff(user):
            return is_flag_active(request, flag_name, organisation=organisation)
        return True

    @staticmethod
    def org_access_denied():
        return JsonResponse(
            {"ok": False, "error": "You do not have access to this organisation."},
            status=403,
        )

    @staticmethod
    def get_ungrouped_organizations(user):
        access_code_exists = OrganisationAccessCode.objects.filter(
            organisation_id=OuterRef("pk")
        ).exclude(code__isnull=True).exclude(code="")
        collection_language_exists = SiteLanguages.objects.filter(
            organisation_id=OuterRef("pk")
        ).exclude(code__isnull=True).exclude(code="")

        return (
            OrganizationService.get_allowed_orgs(user)
            .filter(organization_group__isnull=True)
            .exclude(display_name__isnull=True)
            .exclude(display_name="")
            .exclude(content_collection__isnull=True)
            .exclude(content_collection="")
            .exclude(default_collection_language__isnull=True)
            .exclude(default_collection_language="")
            .exclude(big_icon__isnull=True)
            .exclude(big_icon="")
            .exclude(small_icon__isnull=True)
            .exclude(small_icon="")
            .annotate(
                has_access_code=Exists(access_code_exists),
                has_collection_language=Exists(collection_language_exists),
            )
            .filter(has_access_code=True, has_collection_language=True)
        )

    @staticmethod
    def build_organisation_form_payload(*, organisation):
        return {
            "id": organisation.id,
            "name": organisation.name,
            "org_code": organisation.org_code,
            "access_code": ",".join(
                access_code
                for access_code in organisation.organisation_access_codes.order_by("code")
                .values_list("code", flat=True)
                if access_code
            ),
            "display_name": organisation.display_name,
            "has_custom_content": organisation.has_custom_content,
            "content_collection": organisation.content_collection,
            "work_sector": organisation.work_sector,
            "custom_type": organisation.custom_type,
            "theme": organisation.theme,
            "collection_languages": list(
                organisation.collection_languages.order_by("code").values_list("code", flat=True)
            ),
            "default_collection_language": organisation.default_collection_language,
            "default_report_issue_emails": organisation.default_report_issue_emails,
            "default_feedback_emails": organisation.default_feedback_emails,
            "cms_id": organisation.cms_id,
            "cms_sync_status": organisation.cms_sync_status,
            "last_cms_sync_date": organisation.last_cms_sync_date,
            "big_icon_url": organisation.big_icon or "",
            "big_icon_cms_media_id": organisation.big_icon_cms_media_id,
            "small_icon_url": organisation.small_icon or "",
            "small_icon_cms_media_id": organisation.small_icon_cms_media_id,
        }

    @staticmethod
    def build_icon_upload_name(*, icon_field, org_name, original_name):
        safe_org_name = slugify(org_name).replace("-", "_")
        safe_original_name = (original_name or "image").replace(" ", "_")
        return f"{icon_field}_{safe_org_name}_{safe_original_name}"

    @staticmethod
    def upload_org_icons(*, org_name, big_icon_file=None, small_icon_file=None):
        files_to_upload = []
        uploaded_icons = {}
        if big_icon_file:
            big_icon_name = OrganizationService.build_icon_upload_name(
                icon_field="big_icon",
                org_name=org_name,
                original_name=big_icon_file.name,
            )
            big_icon_file.name = big_icon_name
            files_to_upload.append(big_icon_file)

        if small_icon_file:
            small_icon_name = OrganizationService.build_icon_upload_name(
                icon_field="small_icon",
                org_name=org_name,
                original_name=small_icon_file.name,
            )
            small_icon_file.name = small_icon_name
            files_to_upload.append(small_icon_file)

        if not files_to_upload:
            return uploaded_icons

        uploaded_files = upload_files_to_cms(files_to_upload)
        for uploaded_file in uploaded_files:
            uploaded_name = uploaded_file.get("name", "")
            if uploaded_name.startswith("big_icon"):
                uploaded_icons["big_icon"] = uploaded_file
            elif uploaded_name.startswith("small_icon"):
                uploaded_icons["small_icon"] = uploaded_file

        if big_icon_file and "big_icon" not in uploaded_icons:
            raise FileUploadError("Failed to upload big icon.")

        if small_icon_file and "small_icon" not in uploaded_icons:
            raise FileUploadError("Failed to upload small icon.")

        return uploaded_icons

    @staticmethod
    def create_organization_group(*, form, user):
        organization_group = form.save(commit=False)
        organization_group.created_by = user
        organization_group.updated_by = user
        organization_group.save()
        return organization_group

    @staticmethod
    def get_organization_group(*, organization_group_id):
        return (
            OrganizationGroup.objects.prefetch_related("organizations")
            .filter(id=organization_group_id)
            .first()
        )

    @staticmethod
    def build_organization_group_context(*, organization_group):
        return {
            "organization_group": organization_group,
            "organizations": organization_group.organizations.order_by("name"),
        }

    @staticmethod
    def attach_organizations_to_group(*, organization_group, organizations, user):
        for organization in organizations:
            if not isinstance(organization, OrganisationData):
                continue
            organization.organization_group = organization_group
            organization.updated_by = user
            organization.save(update_fields=["organization_group", "updated_by", "updated_at"])

    @staticmethod
    def add_collection_languages(*, organization, languages, user):
        selected_codes = {language.code for language in languages}
        existing_languages = {
            item.code: item
            for item in SiteLanguages.all_objects.filter(organisation=organization)
        }

        for language in languages:
            site_language = existing_languages.get(language.code)
            language_name = getattr(language, "translated_name", None) or language.name
            if site_language:
                site_language.name = language_name
                if site_language.is_deleted:
                    site_language.is_deleted = False
                    site_language.deleted_at = None
                    site_language.deleted_by = None
                site_language.updated_by = user
                site_language.save()
            else:
                SiteLanguages.objects.create(
                    organisation=organization,
                    code=language.code,
                    name=language_name,
                    created_by=user,
                    updated_by=user,
                )

        for code, site_language in existing_languages.items():
            if code not in selected_codes and not site_language.is_deleted:
                site_language.soft_delete(user)

    @staticmethod
    def add_org_access_code(*, organisation, access_code, user):
        org_access_code = (
            OrganisationAccessCode.objects.filter(organisation=organisation)
            .order_by("created_at", "id")
            .first()
        )
        duplicate_qs = OrganisationAccessCode.objects.filter(code__iexact=access_code)
        if org_access_code:
            duplicate_qs = duplicate_qs.exclude(pk=org_access_code.pk)
        if duplicate_qs.exists():
            raise ValidationError({"access_code": ["Access code already exists."]})

        if org_access_code:
            org_access_code.code = access_code
            org_access_code.updated_by = user
            org_access_code.save(update_fields=["code", "updated_by", "updated_at"])
            return org_access_code

        return OrganisationAccessCode.objects.create(
            organisation=organisation,
            code=access_code,
            created_by=user,
            updated_by=user,
        )
