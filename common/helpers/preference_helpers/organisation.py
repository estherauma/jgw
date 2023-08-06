import re

def normalize_organisation_name(org: str) -> str:
    if org is None:
        return org
    
    patterns_to_replace = {
        'seasonal worker scheme - agri hr':'seasonal worker scheme - agri-hr',
        'seasonal worker scheme - generic': 'seasonal worker scheme - sws generic'
    }
    return patterns_to_replace.get(org.lower(), org).lower()

def format_org_name_from_display(name) -> str:
    # remove the 'seasonal worker scheme - ' prefix
    pattern = re.compile(r'seasonal\s*worker\s*scheme\s*-\s*', re.IGNORECASE)
    return pattern.sub('', name)