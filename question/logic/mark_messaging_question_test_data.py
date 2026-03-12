"""
Logic for marking MessagingQuestionStandard instances as test data based on question_id.
"""

from question.models import MessagingQuestionStandard
from common.const.value_const import MESSAGING_QUESTION_TEST_IDS


def mark_messaging_question_standard_test_data():
    """
    For every MessagingQuestionStandard instance, set is_test_data=True when
    question_id is in the test question ID list, otherwise set is_test_data=False.
    Returns (updated_count_marked_true, updated_count_marked_false).
    """
    to_mark_true = MessagingQuestionStandard.objects.filter(
        question_id__in=MESSAGING_QUESTION_TEST_IDS,
        is_test_data=False
    )
  
    updated_count = to_mark_true.update(is_test_data=True)

    return updated_count
