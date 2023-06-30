# route is in this format:  UGA -> UGA
from common.const.value_const import NOT_SPECIFIED


def get_origin_and_destination_from_route(route: str) -> dict[str, str]:
    if route == NOT_SPECIFIED:
        return { "origin" :NOT_SPECIFIED, "destination": NOT_SPECIFIED}
    else:
        origin, destination = route.split(" -> ")
        return { "origin" : origin, "destination": destination}