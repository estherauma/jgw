from common.const.value_const import NOT_SPECIFIED


def normalize_country_name(country: str) -> str:
    country_mapping = {
        "saudi": "saudi arabia",
        "saudi arabia": "saudi arabia",
        "uae": "united arab emirates",
        "united arab emirates": "united arab emirates",
        "uk": "united kingdom",
        "gbr": "united kingdom",
        "united kingdom": "united kingdom",
        "zzz": "other - the rest of the world",
        "viet nam": "vietnam",
        "vnm": "vietnam",
        "": NOT_SPECIFIED,
        " ": NOT_SPECIFIED,
        "null": NOT_SPECIFIED,
    }

    if country is None:
        return NOT_SPECIFIED.lower()

    normalized_country = country_mapping.get(country.lower(), country)

    if not normalized_country.strip():
        normalized_country = NOT_SPECIFIED

    return normalized_country.lower().strip()


def get_origin_and_destination_from_route(route: str) -> dict[str, str]:
    if route == NOT_SPECIFIED:
        return {"origin": NOT_SPECIFIED, "destination": NOT_SPECIFIED}
    else:
        origin, destination = route.split(" -> ")
        return {"origin": origin, "destination": destination}


def get_data_origin(route, api_origin):
    origin_from_route = get_origin_and_destination_from_route(route).get("origin")
    return origin_from_route if origin_from_route != "not specified" else api_origin


def get_data_destination(route, api_destination, location_of_potential_work):
    if api_destination:
        return api_destination

    if location_of_potential_work:
        return location_of_potential_work

    if route:
        return get_origin_and_destination_from_route(route).get("destination")
