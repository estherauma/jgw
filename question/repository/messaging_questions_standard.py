from question.filters import generic_question_filtered_queryset
from question.models import InlineQuestionResponse, InlineQuestionResponseText, MessagingQuestionStandard
from django.db.models import Count, Case, When, F


def get_messaging_question_per_origin_counts(**filters):
    
    queryset = generic_question_filtered_queryset(
        queryset = MessagingQuestionStandard.objects.all(), 
        **filters
    )
        
    origin_counts_data = queryset.annotate(
        origin_name=Case(
            When(preference__isnull=False, then=F('preference__origin__name')),
            default=F('origin__name')
        )
    ).values(
        'origin__name'
    ).annotate(
        count=Count('origin__name')
    ).order_by('-count')
    
    origin_data = [count['count'] for count in origin_counts_data]
    origin_labels = [count['origin__name'].upper() for count in origin_counts_data if count['origin__name'] is not None]
    
    return {
            "counts": origin_data,
            "labels": origin_labels,
        }


def get_messaging_question_per_destination_counts(**filters):  
        
    queryset = generic_question_filtered_queryset(
        queryset = MessagingQuestionStandard.objects.all(), 
        **filters
    )
     
    destination_counts_data = queryset.annotate(
        destination_name=Case(
            When(preference__isnull=False, then=F('preference__destination__name')),
            default=F('destination__name')
        )
    ).values(
        'destination__name'
    ).annotate(
        count=Count('destination__name')
    ).order_by('-count')
    
    
    destination_data = [count['count'] for count in destination_counts_data]
    destination_labels = [count['destination__name'].upper() for count in destination_counts_data if count['destination__name'] is not None]
    
    return {
            "counts": destination_data,
            "labels": destination_labels,
        }
    


def messaging_questions_count(**filters):
    
    messaging_questions_count_queryset = generic_question_filtered_queryset(
        queryset = MessagingQuestionStandard.objects.all(), 
        **filters
    )
        
    return messaging_questions_count_queryset.count()


def messaging_question_stats_for_export(filters):
    messaging_question_per_origin = get_messaging_question_per_origin_counts(**filters)
    messaging_question_per_destination = get_messaging_question_per_destination_counts(**filters)
    return {
        "responses_per_origin": messaging_question_per_origin,
        "responses_per_destination": messaging_question_per_destination,
    }