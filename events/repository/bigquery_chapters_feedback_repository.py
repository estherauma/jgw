from collections import defaultdict
from django.db.models import Count, Sum

from events.models import ChaptersFeedback, ChaptersFeedbackStandard


def get_chapters_feedback():
    """ Aggregates chapters feedback and returns a disctionary

    Returns:
        dict: a dictionary containing the aggregated chapters feedback
        {
            'question': str,  # The question.
            'data': {
                'labels': list of str,  # Labels associated with the feedback.
                'counts': list of int   # Corresponding counts for each label.
            }
        }
        
    Example:
        {
            'question': 'wasThisHelpful',
            'data': {
                'labels': ['smile', 'frown'],
                'counts': [808, 81]
            }
        }
    """
    result = ChaptersFeedback.objects.values(
        'feedback_question__question',
        'feedback_response__translated_response'
    ).annotate(count=Count('id')).order_by('-count')    
        
    feedback_dict = {}
    for item in result:
        question = item['feedback_question__question']
        response = item['feedback_response__translated_response']
        count = item['count']
        
        if question not in feedback_dict:
            feedback_dict[question] = {'response': [response], 'count': [count]}
        else:
            feedback_dict[question]['response'].append(response)
            feedback_dict[question]['count'].append(count)

    formatted_data = [{'question': key, 'data': {'labels': val['response'], 'counts': val['count']}} for key, val in feedback_dict.items()]

    return formatted_data
