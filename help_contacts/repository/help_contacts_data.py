from help_contacts.models import HelpContact
from django.db.models import Q


def get_help_contacts_between_dates(**filters):
    """
    Returns HelpContact instances between the given start_date and end_date.
    
    Args:
        start_date (datetime): The start date of the range.
        end_date (datetime): The end date of the range.

    Returns:
        QuerySet: A queryset of HelpContact instances with the specified fields.
    """
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    origin_names = filters.get('origin_countries', [])
    destination_names = filters.get('destination_countries', [])
    
    query= Q()
    if start_date and end_date:
        query = Q(api_created_at__range=(start_date, end_date))

    if origin_names:
        query &= Q(origin__name__in=origin_names)
    
    if destination_names:
        query &= Q(destination__name__in=destination_names)

    return HelpContact.objects.filter(query).values(
        'api_created_at', 'contact_type', 'device_id', 
        'locale', 'translated_contact_value', 'origin__name', 'destination__name'
    )