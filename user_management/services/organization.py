from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db.models import Exists, OuterRef, Q
from django.core.paginator import Paginator

from content.services.partner_configurations import FileUploadError, upload_files_to_cms
from content.models import WorkSector
from preference.models import (
    Country,
    ImmigrationStatus,
    OrganizationGroup,
    OrganisationAccessCode,
    OrganisationData,
    OrganisationDeepLink,
    SiteLanguages,
)
from .deep_links import DeepLinkService
from user_management.permissions import is_flag_active
from user_management.utils import is_org_admin_or_staff, is_org_group_admin, is_super_or_58_admin
from ..forms import OrganisationDeepLinkForm


class OrganizationService:
    @staticmethod
    def serialize_email_list(raw_value):
        if not raw_value:
            return []
        return [
            email.strip()
            for email in str(raw_value).split(",")
            if email and email.strip()
        ]

    @staticmethod
    def serialize_work_sector(raw_value):
        value = (raw_value or "").strip()
        if not value:
            return ""
        if " (" in value and value.endswith(")"):
            return value.split(" (", 1)[0].strip()
        return value

    @staticmethod
    def serialize_default_collection_language(raw_value):
        value = (raw_value or "").strip()
        if not value:
            return ""
        if " (" in value and value.endswith(")"):
            return value.split(" (", 1)[0].strip()
        return value

    @staticmethod
    def serialize_collection_languages(*, organisation):
        languages = getattr(organisation, "_prefetched_objects_cache", {}).get(
            "collection_languages"
        )
        if languages is None:
            languages = organisation.collection_languages.all()
        return [
            {
                "code": language.code,
                "name": language.name,
            }
            for language in languages
        ]

    @staticmethod
    def serialize_access_codes(*, organisation):
        access_codes = getattr(organisation, "_prefetched_objects_cache", {}).get(
            "organisation_access_codes"
        )
        if access_codes is None:
            access_codes = organisation.organisation_access_codes.all()
        return [
            {
                "id": access_code.id,
                "code": access_code.code,
                "requires_login": access_code.requires_login,
                "expiry_date": access_code.expiry_date.isoformat()
                if access_code.expiry_date
                else None,
            }
            for access_code in access_codes
        ]

    @staticmethod
    def serialize_user_groups(*, organisation):
        work_groups = getattr(organisation, "_prefetched_objects_cache", {}).get(
            "work_groups"
        )
        if work_groups is None:
            work_groups = organisation.work_groups.all()
        return [
            {
                "id": work_group.id,
                "name": work_group.name,
            }
            for work_group in work_groups
        ]

    @staticmethod
    def build_partner_config_payload(*, organisation):
        return {
            "id": organisation.id,
            "name": organisation.name,
            "org_code": organisation.org_code,
            "display_name": organisation.display_name,
            "has_custom_content": organisation.has_custom_content,
            "theme": organisation.theme,
            "custom_type": organisation.custom_type,
            "work_sector": OrganizationService.serialize_work_sector(
                organisation.work_sector
            ),
            "content_collection": organisation.content_collection,
            "default_collection_language": OrganizationService.serialize_default_collection_language(
                organisation.default_collection_language
            ),
            "default_feedback_emails": organisation.default_feedback_emails,
            "default_report_issue_emails": organisation.default_report_issue_emails,
            "cms_id": organisation.cms_id,
            "cms_sync_status": organisation.cms_sync_status,
            "last_cms_sync_date": organisation.last_cms_sync_date.isoformat()
            if organisation.last_cms_sync_date
            else None,
            "collection_languages": OrganizationService.serialize_collection_languages(
                organisation=organisation
            ),
            "access_codes": OrganizationService.serialize_access_codes(
                organisation=organisation
            ),
            "user_groups": OrganizationService.serialize_user_groups(
                organisation=organisation
            ),
            "big_icon_url": organisation.big_icon or "",
            "small_icon_url": organisation.small_icon or "",
        }

    @staticmethod
    def get_access_code_record(*, access_code, include_workgroups=False):
        normalized_code = (access_code or "").strip().upper()
        if not normalized_code:
            return None

        query = OrganisationAccessCode.objects.select_related("organisation")
        if include_workgroups:
            query = query.prefetch_related("work_groups")

        work_code = query.filter(code__iexact=normalized_code).first()
        if not work_code:
            return None

        organisation = work_code.organisation
        if not organisation or organisation.is_deleted:
            return None
        return work_code

    @staticmethod
    def get_access_code_status(*, access_code):
        work_code = OrganizationService.get_access_code_record(access_code=access_code)
        if not work_code:
            return None
        return {
            "code": work_code.code,
            "requires_login": work_code.requires_login,
        }

    @staticmethod
    def get_access_code_details(*, access_code, user=None):
        work_code = OrganizationService.get_access_code_record(
            access_code=access_code,
            include_workgroups=True,
        )
        if not work_code:
            return None

        organisation = work_code.organisation
        access_code_user_groups = list(work_code.work_groups.order_by("name"))
        visible_user_groups = access_code_user_groups

        if user is not None and getattr(user, "is_authenticated", False):
            user_work_group_ids = set(
                user.work_groups.filter(organisation=organisation).values_list("id", flat=True)
            )
            visible_user_groups = [
                work_group
                for work_group in access_code_user_groups
                if work_group.id in user_work_group_ids
            ]

        serialized_access_code_user_groups = [
            {
                "id": work_group.id,
                "name": work_group.name,
            }
            for work_group in visible_user_groups
        ]
        return {
            "id": work_code.id,
            "code": work_code.code,
            "requires_login": work_code.requires_login,
            "expiry_date": work_code.expiry_date.isoformat() if work_code.expiry_date else None,
            "organization": 
                {
                    "id": organisation.id,
                    "name": organisation.name,
                    "org_code": organisation.org_code,
                    "display_name": organisation.display_name,
                    "has_custom_content": organisation.has_custom_content,
                    "theme": organisation.theme,
                    "custom_type": organisation.custom_type,
                    "work_sector": OrganizationService.serialize_work_sector(
                        organisation.work_sector
                    ),
                    "content_collection": organisation.content_collection,
                    "default_collection_language": OrganizationService.serialize_default_collection_language(
                        organisation.default_collection_language
                    ),
                    "default_feedback_emails": OrganizationService.serialize_email_list(
                        organisation.default_feedback_emails
                    ),
                    "default_report_issue_emails": OrganizationService.serialize_email_list(
                        organisation.default_report_issue_emails
                    ),
                    "collection_languages": OrganizationService.serialize_collection_languages(
                        organisation=organisation
                    ),
                    "big_icon_url": organisation.big_icon or "",
                    "small_icon_url": organisation.small_icon or "",
                },
            "access_code_user_groups": serialized_access_code_user_groups,
        }

    @staticmethod
    def get_partner_configs():
        organisations = OrganisationData.objects.prefetch_related(
            "collection_languages",
            "organisation_access_codes",
            "work_groups",
        )
        return [
            OrganizationService.build_partner_config_payload(organisation=organisation)
            for organisation in organisations
        ]

    @staticmethod
    def get_allowed_orgs(user):
        if user.is_anonymous:
            return OrganisationData.objects.none()
        if is_super_or_58_admin(user):
            return OrganisationData.objects.all()
        if is_org_group_admin(user):
            organization_group_id = getattr(user, "organization_group_id", None)

            if not organization_group_id:
                return OrganisationData.objects.none()
            return OrganisationData.objects.filter(
                organization_group_id=organization_group_id
            )
        if is_org_admin_or_staff(user):
            org = user.organisation_data.order_by("name").first()
            if not org:
                return OrganisationData.objects.none()
            return OrganisationData.objects.filter(id=org.id)
        return OrganisationData.objects.none()

    @staticmethod
    def get_allowed_organization_group(user):
        if user.is_anonymous:
            return None
        if is_super_or_58_admin(user):
            return None
        if getattr(user, "organization_group_id", None):
            return user.organization_group
        group_org = (
            user.organisation_data.select_related("organization_group")
            .filter(organization_group__isnull=False)
            .order_by("organization_group__name", "name")
            .first()
        )
        if not group_org:
            return None
        return group_org.organization_group

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
    def create_login_deep_link(
        *,
        user,
        request,
        organisation=None,
        work_code_id=None,
    ):
        if not work_code_id:
            raise ValueError("Work code is required.")

        allowed_orgs = OrganizationService.get_allowed_orgs(user)
        work_code_filters = {
            "id": work_code_id,
            "organisation__in": allowed_orgs,
        }
        if organisation:
            work_code_filters["organisation"] = organisation

        work_code = (
            OrganisationAccessCode.objects.select_related("organisation")
            .filter(**work_code_filters)
            .first()
        )

        if not work_code:
            raise ValueError("Work code not found.")

        if not OrganizationService.has_org_access(
            user,
            organisation or work_code.organisation,
            request=request,
            flag_name="can_edit_work_code",
        ):
            raise PermissionError("You do not have access to this organisation.")

        return DeepLinkService.get_or_create_login__deep_link(work_code=work_code)

    @staticmethod
    def create_onboarding_deep_link(
        *,
        organisation=None,
        payload=None,
    ):
        payload = payload or {}
        if not organisation:
            org_id = payload.get("selected_org_id")
            if org_id:
                organisation = OrganisationData.objects.filter(id=org_id).first()
        if not organisation:
            raise ValidationError(
                {"organisation": ["Select an organisation first."]}
            )

        form = OrganisationDeepLinkForm(payload, organisation=organisation)
        if not form.is_valid():
            raise ValidationError(form.errors)

        link_data = {
            "title": form.cleaned_data["title"],
            "link_type": form.cleaned_data["link_type"],
            "destination": form.cleaned_data["destination"],
            "access_code": form.cleaned_data.get("access_code"),
            "sector": form.cleaned_data.get("sectors"),
            "immigration_status": form.cleaned_data.get("immigration_status"),
        }

        branch_data = DeepLinkService.create_onboarding_deep_link(
            organisation=organisation,
            link_data=link_data,
        )
        branch_url = branch_data["url"]
        deep_link = form.save(generated_link=branch_url)
        return {
            "deep_link_id": deep_link.id,
            "org_id": organisation.id,
            "title": deep_link.title,
            "url": branch_url,
            "data": branch_data["data"],
        }

    @staticmethod
    def get_organisation_deep_link_prefill(*, organisation, deep_link_id):
        deep_link = OrganisationDeepLink.objects.filter(
            id=deep_link_id,
            organisation=organisation,
        ).first()
        if not deep_link:
            raise ValueError("Deep link not found.")
        if not deep_link.link:
            raise ValueError("Deep link URL not found.")

        branch_data = DeepLinkService.get_branch_deep_link(branch_url=deep_link.link)
        branch_link_data = branch_data.get("data") or {}
        print(branch_link_data)

        destination = Country.objects.filter(
            code__iexact=(branch_link_data.get("destination") or "").strip()
        ).first()
        access_code = OrganisationAccessCode.objects.filter(
            organisation=organisation,
            code__iexact=(branch_link_data.get("organisationAccessCode") or "").strip(),
        ).first()
        sector = WorkSector.objects.filter(
            slug=(branch_link_data.get("sectors") or "").strip()
        ).first()
        immigration_status = ImmigrationStatus.objects.filter(
            value=(branch_link_data.get("immigrationStatus") or "").strip()
        ).first()

        return {
            "deep_link_id": deep_link.id,
            "title": (
                branch_link_data.get("$marketing_title")
                or branch_link_data.get("title")
                or deep_link.title
            ),
            "link_type": (
                branch_link_data.get("type")
                or deep_link.link_type
                or "onboarding"
            ),
            "destination": str(destination.id) if destination else "",
            "access_code": str(access_code.id) if access_code else "",
            "sectors": sector.slug if sector else "",
            "immigration_status": str(immigration_status.id) if immigration_status else "",
        }

    @staticmethod
    def update_onboarding_deep_link(
        *,
        organisation,
        deep_link_id,
        payload=None,
    ):
        payload = payload or {}
        deep_link = OrganisationDeepLink.objects.filter(
            id=deep_link_id,
            organisation=organisation,
        ).first()
        if not deep_link:
            raise ValueError("Deep link not found.")

        form = OrganisationDeepLinkForm(
            payload,
            organisation=organisation,
            instance=deep_link,
        )
        if not form.is_valid():
            raise ValidationError(form.errors)

        link_data = {
            "title": form.cleaned_data["title"],
            "link_type": form.cleaned_data["link_type"],
            "destination": form.cleaned_data["destination"],
            "access_code": form.cleaned_data.get("access_code"),
            "sector": form.cleaned_data.get("sectors"),
            "immigration_status": form.cleaned_data.get("immigration_status"),
        }

        branch_data = DeepLinkService.update_onboarding_deep_link(
            organisation=organisation,
            deep_link=deep_link,
            link_data=link_data,
        )
        updated_deep_link = form.save(generated_link=branch_data["url"])
        return {
            "deep_link_id": updated_deep_link.id,
            "org_id": organisation.id,
            "title": updated_deep_link.title,
            "url": branch_data["url"],
            "data": branch_data["data"],
        }

    @staticmethod
    def delete_organisation_deep_link(*, organisation, deep_link_id):
        deep_link = OrganisationDeepLink.objects.filter(
            id=deep_link_id,
            organisation=organisation,
        ).first()
        if not deep_link:
            raise ValueError("Deep link not found.")

        if deep_link.link:
            DeepLinkService.delete_branch_deep_link(branch_url=deep_link.link)

        deep_link_title = deep_link.title
        deep_link.delete()
        return {
            "org_id": organisation.id,
            "title": deep_link_title,
        }

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
    def get_organisation_deep_links(*, organisation):
        deep_links = OrganisationDeepLink.objects.filter(
            organisation=organisation
        ).order_by("created_at")
        for deep_link in deep_links:
            deep_link.qr_code_url = (
                DeepLinkService.create_qr_code(deep_link=deep_link.link)
                if deep_link.link
                else ""
            )
        return deep_links

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
            "organization_group": organisation.organization_group.name
            if organisation.organization_group
            else "",
            "has_custom_content": organisation.has_custom_content,
            "content_collection": organisation.content_collection,
            "work_sector": OrganizationService.serialize_work_sector(
                organisation.work_sector
            ),
            "custom_type": organisation.custom_type,
            "theme": organisation.theme,
            "collection_languages": list(
                organisation.collection_languages.order_by("code").values_list("code", flat=True)
            ),
            "default_collection_language": OrganizationService.serialize_default_collection_language(
                organisation.default_collection_language
            ),
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
    def edit_organization_group(*, form, user):
        organization_group = form.save(commit=False)
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
    def remove_organization_from_group(*, organization, user):
        organization.organization_group = None
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

    @staticmethod
    def filter_organisations_query(queryset, query=""):
        query = (query or "").strip()
        if not query:
            return queryset
        return queryset.filter(
            Q(name__icontains=query) | Q(org_code__icontains=query)
        )
    
    @staticmethod
    def get_paginated_organisations_context(user, query="", page_number=None):
        queryset = OrganizationService.get_allowed_orgs(user).order_by("name")
        queryset = OrganizationService.filter_organisations_query(
            queryset,
            query=query,
        )
        paginator = Paginator(queryset, 20)
        organisations_page = paginator.get_page(page_number)

        return {
            "organisations": list(organisations_page.object_list),
            "organizations_page": organisations_page,
            "organizations_pagination_context": {
                "page_obj": organisations_page,
                "page_numbers": list(
                    organisations_page.paginator.get_elided_page_range(
                        organisations_page.number
                    )
                ),
                "item_label": "organisations",
                "nav_label": "Organisations pagination",
                "page_link_attr": "data-org-page-link",
            },
            "organizations_row_start_index": (
                organisations_page.start_index()
                if organisations_page.object_list
                else 0
            ),
        }
