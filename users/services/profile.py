from preference.models import OrganisationAccessCode


def _serialize_access_code(access_code):
    return {
        "id": access_code.id,
        "code": access_code.code,
        "requires_login": access_code.requires_login,
        "expiry_date": access_code.expiry_date.isoformat() if access_code.expiry_date else None,
    }


def get_current_user_payload(user):
    organisation = user.organisation_data.order_by("name").first()
    user_groups = []
    organisation_payload = None
    accessible_access_codes = []
    role = user.groups.order_by("name").values_list("name", flat=True).first()

    if organisation:
        user_work_groups = user.work_groups.filter(organisation=organisation).order_by("name")
        user_groups = [
            {
                "id": work_group.id,
                "name": work_group.name,
            }
            for work_group in user_work_groups
        ]

        organisation_access_codes = (
            OrganisationAccessCode.objects.prefetch_related("work_groups")
            .filter(organisation=organisation)
            .order_by("code")
        )
        user_work_group_ids = list(user_work_groups.values_list("id", flat=True))
        accessible_access_codes = [
            _serialize_access_code(access_code)
            for access_code in organisation_access_codes
            if not access_code.work_groups.exists()
            or access_code.work_groups.filter(id__in=user_work_group_ids).exists()
        ]

        organisation_payload = {
            "id": organisation.id,
            "name": organisation.name,
            "org_code": organisation.org_code,
            "display_name": organisation.display_name,
            "user_groups": user_groups,
            "access_codes": accessible_access_codes,
        }

    return {
        "id": user.id,
        "email": user.email,
        "phone_number": user.phone_number,
        "phone_country_iso": user.phone_country_iso,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": role,
        "access_type": user.access_type,
        "is_active": user.is_active,
        "organisation": organisation_payload,
    }
