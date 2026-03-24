import re
from typing import Optional, Union

from common.const.value_const import NOT_SPECIFIED, org_info_list
from preference.models import OrganisationData

def normalize_organisation_name(org: str) -> str:    
    patterns_to_replace = {
        'seasonal worker scheme - agri hr':'seasonal worker scheme - agri-hr',
        'seasonal worker scheme - generic': 'seasonal worker scheme - sws generic',
        '': NOT_SPECIFIED,
        ' ': NOT_SPECIFIED,
    }
    
    if org is None:
        return NOT_SPECIFIED.lower()
    
    normalized_org = patterns_to_replace.get(org.lower(), org).lower()
    
    if not normalized_org.strip():
        normalized_org = NOT_SPECIFIED
        
    return normalized_org.lower()
    

def format_org_name_from_display(name):
    if not name: 
        return ""
    pattern = re.compile(r'[^\w\s-]')
    return pattern.sub('', name)


def get_organisation_data(
    org_code: Optional[str] = None,
    organisation: Optional[Union["Organisation", str]] = None,
) -> OrganisationData:
    """
    Return the OrganisationData instance for the given org_code and/or organisation.

    Resolution order:
    1. If org_code is not null/empty: look up OrganisationData by org_code and return it.
    2. Else if organisation is not null: match by organisation name (via org_info_list)
       and return the corresponding OrganisationData.
    3. Otherwise: return OrganisationData with code ONS.

    Reusable across the application for resolving org_info from org_code or organisation name.

    :param org_code: Optional organisation code string (e.g. from Preference.org_code).
    :param organisation: Optional Organisation model instance or organisation name string.
    :return: OrganisationData instance (never None).
    """
    if org_code and org_code.strip():
        try:
            return OrganisationData.objects.get(org_code=org_code.strip())
        except OrganisationData.DoesNotExist:
            pass

    org_name = None
    if organisation is not None:
        if hasattr(organisation, "name"):
            org_name = (organisation.name or "").lower().strip()
        elif isinstance(organisation, str):
            org_name = organisation.lower().strip()
    if org_name:
        matching_org = next(
            (org for org in org_info_list if (org.get("name") or "").lower().strip() == org_name),
            None,
        )
        if matching_org:
            try:
                return OrganisationData.objects.get(org_code=matching_org["org_code"])
            except OrganisationData.DoesNotExist:
                pass

    return OrganisationData.objects.get(org_code="ONS")