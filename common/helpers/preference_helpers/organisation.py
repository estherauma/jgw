import re

from common.const.value_const import NOT_SPECIFIED

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
    

def format_org_name_from_display(name) -> str:
    # remove the 'seasonal worker scheme - ' prefix
    pattern = re.compile(r'seasonal\s*worker\s*scheme\s*-\s*', re.IGNORECASE)
    return pattern.sub('', name)