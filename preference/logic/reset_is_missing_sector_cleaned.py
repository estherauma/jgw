
from preference.models import Preference


def reset_is_missing_sector_cleaned_in_the_preference_table():
    """
    Reset is_missing_sector_cleaned column in Preference table to default (False)
    """
    Preference.objects.all().update(is_missing_sector_cleaned=False)
