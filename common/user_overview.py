from common.inline import Inline
from common.preferences import Preferences
from common.utils.dictionary_utils import add_prefix_to_dictionary_keys, combine_dictionaries


def get_user_overview_data(filters):
    preferences = Preferences()
    inline = Inline()
    
    preferences_question_overview_stats = add_prefix_to_dictionary_keys(
        preferences.compute_stats(filters=filters),
        prefix="preference"
    )
    inline_question_overview_stats = add_prefix_to_dictionary_keys(
        inline.overview_stats(filters=filters),
        prefix="inline_question"
    )
    
    user_overview_dictionary = combine_dictionaries(
        preferences_question_overview_stats,
        inline_question_overview_stats
    )
    
    return user_overview_dictionary