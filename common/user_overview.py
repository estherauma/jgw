from common.inline import Inline
from common.preferences import Preferences
from common.utils.dictionary_utils import add_prefix_to_dictionary_keys, combine_dictionaries


def get_user_overview_data(filters):
    preferences = Preferences()
    
    preferences_question_overview_stats = add_prefix_to_dictionary_keys(
        dictionary = preferences.compute_stats(filters=filters),
        prefix = "preference"
    )
    
    return preferences_question_overview_stats