from common.const.value_const import NOT_SPECIFIED

def normalize_country_name(country: str) -> str:
    if country is None:
        return country
    
    country_mapping = {
        'saudi': 'saudi arabia',
        'saudi arabia': 'saudi arabia',
        'uae': 'united arab emirates',
        'united arab emirates': 'united arab emirates',
        'uk': 'united kingdom',
        'united kingdom': 'united kingdom',
    }
    return country_mapping.get(country.lower(), country).lower()

    
def get_origin_and_destination_from_route(route: str) -> dict[str, str]:
    if route == NOT_SPECIFIED:
        return { "origin" : NOT_SPECIFIED, "destination": NOT_SPECIFIED}
    else:
        origin, destination = route.split(" -> ")
        return { 
                "origin" : normalize_country_name(origin), 
                "destination": normalize_country_name(destination)
            }