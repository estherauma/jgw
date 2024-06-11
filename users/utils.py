from django.db.models import Q

from preference.models import Country, FactoryFarm, Language, Organisation


def get_user_factories(user):
    if user.is_anonymous or user.role == "ADMIN" or user.is_superuser:
        return FactoryFarm.objects.all()
    return user.factories.all()


def get_user_organisations(user):
    if user.is_anonymous or user.role == "ADMIN" or user.is_superuser:
        return Organisation.objects.all()
    return user.organisations.all()


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