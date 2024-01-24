from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from common.utils.strings import format_thousands_with_commas

from events.models import SwsPasiEvent
from users.utils import get_user_organisations


def get_total_dynamic_link_usage(current_user):
    user_orgs = get_user_organisations(current_user)
    return format_thousands_with_commas(SwsPasiEvent.objects.filter(organisation__in=user_orgs).count())
