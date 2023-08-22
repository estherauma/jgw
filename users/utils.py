from django.shortcuts import get_object_or_404

from users.models import User


def get_user_factories(user):
    return user.factories.all()


def get_user_organisations(user):
    return user.organisations.all()