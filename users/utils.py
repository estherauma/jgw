from django.db.models import Q

from preference.models import Country, FactoryFarm, Organisation


def get_user_factories(user):
    if user.is_anonymous or user.role == 'ADMIN' or user.is_superuser:
        return FactoryFarm.objects.all()
    return user.factories.all()


def get_user_organisations(user):
    if user.is_anonymous or user.role == 'ADMIN' or user.is_superuser:
        return Organisation.objects.all()
    return user.organisations.all()


def get_user_destinations(user):
    exclude_query = Q()
    for country_name in ["test-state", "tstd", "tstl", "viet nam"]:
        exclude_query |= Q(name=country_name)
        
    if user.is_anonymous or user.role == 'ADMIN' or user.is_superuser:
        return Country.objects.filter(is_destination=True).exclude(exclude_query)
    return user.destinations.all()