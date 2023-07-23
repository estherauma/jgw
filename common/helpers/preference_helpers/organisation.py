def normalize_organisation_name(org: str) -> str:
    if org is None:
        return org
    
    patterns_to_replace = {
        'seasonal worker scheme - agri hr':'seasonal worker scheme - agri-hr',
        'seasonal worker scheme - generic': 'seasonal worker scheme - sws generic'
    }
    return patterns_to_replace.get(org.lower(), org).lower()