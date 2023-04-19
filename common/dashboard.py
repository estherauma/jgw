from common.helpers import HELPERS, HelpersParameters


def get_destination_countries_from_preferences():
    helper = HELPERS[HelpersParameters.PREFERENCES.value]()
    print("yessss", helper.get_destination_countries())
    return helper.get_destination_countries()