from django.shortcuts import get_object_or_404

from users.models import User
from preference.models import FactoryFarm, Organisation


def get_user_factories(user):
    if user.is_anonymous or user.role == 'ADMIN':
        return FactoryFarm.objects.all()
    return user.factories.all()


def get_user_organisations(user):
    if user.is_anonymous or user.role == 'ADMIN':
        return Organisation.objects.all()
    return user.organisations.all()