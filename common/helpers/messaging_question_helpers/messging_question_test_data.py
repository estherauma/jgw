"""
Helpers for messaging question logic (e.g. MessagingQuestionStandard creation).
"""

from common.const.value_const import MESSAGING_QUESTION_TEST_IDS


def is_messaging_question_test_data(question_id):
    """
    Return True if the given question_id indicates test data for messaging
    question responses, so is_test_data should be set on MessagingQuestionStandard.
    """
    print(f"question_id: {question_id}")
    if question_id in MESSAGING_QUESTION_TEST_IDS:
        return True
    return False
