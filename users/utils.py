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


def get_user_excepted_languages(user):
    if user.is_anonymous or user.role == "ADMIN" or user.is_superuser:
        return []

    excepted_languages_list = user.excepted_languages.all()
    return excepted_languages_list
