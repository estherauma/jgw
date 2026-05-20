from django.db.models import Q

from preference.models import Country, FactoryFarm, Language, OrganisationData

ALL_GROUPS = [
    "58_admin",
    "org_admin",
    "org_group_admin",
    "org_staff",
    "user_management",
    "worker",
    "testers",
    "my_voice",
    "summer_berry",
    "Summerberry"
]


def get_user_factories(user):
    if user.is_anonymous or user.role == "ADMIN" or user.is_superuser:
        return FactoryFarm.objects.all()
    return user.factories.all()


def get_user_organisations(user):
    if user.is_anonymous or user.role == "ADMIN" or user.is_superuser:
        return OrganisationData.objects.all()
    return user.organisation_data.all()


def get_user_destinations(user):
    exclude_query = Q()
    for country_name in ["test-state", "tstd", "tstl", "viet nam"]:
        exclude_query |= Q(name=country_name)

    if user.is_anonymous or user.role == "ADMIN" or user.is_superuser:
        return Country.objects.filter(is_destination=True).exclude(exclude_query)
    return user.destinations.all()


def get_user_languages(user):
    if user.is_anonymous or user.role == "ADMIN" or user.is_superuser:
        return []

    user_languages_list = user.user_languages.all()
    return user_languages_list


def get_user_excluded_origin_countries(user):
    if user.is_anonymous or user.role == "ADMIN" or user.is_superuser:
        return []

    user_excluded_origin_countries = user.excluded_origin_countries.all()
    return user_excluded_origin_countries


def get_user_start_date(user):
    if user.is_anonymous or user.role == "ADMIN" or user.is_superuser:
        return None
    return user.start_date


def get_user_end_date(user):
    if user.is_anonymous or user.role == "ADMIN" or user.is_superuser:
        return None
    return user.end_date


def get_user_group(user):
    if user.is_anonymous or user.role == "ADMIN" or user.is_superuser:
        return []
    return list(user.groups.values_list("name", flat=True))


def get_user_immigration_status(user):
    """
    Get immigration statuses associated with a user.
    Returns all immigration statuses for admin/superuser, otherwise returns user's configured statuses.

    Args:
        user: User object

    Returns:
        QuerySet of ImmigrationStatus objects
    """
    if user.is_anonymous or user.role == "ADMIN" or user.is_superuser:
        return []

    user_immigration_status = user.immigration_status.all()
    return user_immigration_status
