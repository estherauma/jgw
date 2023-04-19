from common.helpers import HELPERS, HelpersParameters


def get_destination_countries_from_preferences():
    helper = HELPERS[HelpersParameters.PREFERENCES.value]()
    get_destination_countries = helper.get_destination_countries()
    print("helper -----> helper", get_destination_countries)
    return helper.get_destination_countries()