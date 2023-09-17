from common.const.value_const import NOT_SPECIFIED

def normalize_country_name(country: str) -> str:
    country_mapping = {
        'saudi': 'saudi arabia',
        'saudi arabia': 'saudi arabia',
        'uae': 'united arab emirates',
        'united arab emirates': 'united arab emirates',
        'uk': 'united kingdom',
        'gbr': 'united kingdom',
        'united kingdom': 'united kingdom',
        'zzz': 'other - the rest of the world',
        'viet nam':'vietnam',
        '': NOT_SPECIFIED,
        ' ': NOT_SPECIFIED,
    }
    
    if country is None:
        return NOT_SPECIFIED.lower()
    
    normalized_country = country_mapping.get(country.lower(), country)
    
    if not normalized_country.strip():
        normalized_country = NOT_SPECIFIED
        
    return normalized_country.lower().strip()

    
def get_origin_and_destination_from_route(route: str) -> dict[str, str]:
    if route == NOT_SPECIFIED:
        return { "origin" : NOT_SPECIFIED, "destination": NOT_SPECIFIED}
    else:
        origin, destination = route.split(" -> ")
        return { 
                "origin" : origin, 
                "destination": destination
            }