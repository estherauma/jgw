from help_contacts.models import HelpContact


def get_help_contacts_between_dates(start_date, end_date):
    """
    Returns HelpContact instances between the given start_date and end_date.
    
    Args:
        start_date (datetime): The start date of the range.
        end_date (datetime): The end date of the range.

    Returns:
        QuerySet: A queryset of HelpContact instances with the specified fields.
    """
    return HelpContact.objects.filter(
        api_created_at__range=(start_date, end_date)
    ).values(
        'api_created_at', 'contact_type','device_id', 
        'locale', 'translated_contact_value', 'origin__name', 'destination__name'
    )