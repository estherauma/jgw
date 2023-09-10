from collections import defaultdict
from django.db.models import Count, Sum

from events.models import ChaptersFeedback, ChaptersFeedbackStandard


def get_chapters_feedback():
    result = ChaptersFeedback.objects.values(
        'feedback_question__question',
        'feedback_response__translated_response'
    ).annotate(count=Count('id'))    
        
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

    formatted_data = [{'question': key, 'data': {'response': val['response'], 'count': val['count']}} for key, val in feedback_dict.items()]

    return formatted_data
