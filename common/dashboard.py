from common.helpers.common import HELPERS, HelpersParameters


def get_destination_countries_from_preferences():
    helper = HELPERS[HelpersParameters.PREFERENCES.value]()
    return helper.get_destination_countries()