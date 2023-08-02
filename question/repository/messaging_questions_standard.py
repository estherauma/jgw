from common.utils.date_utils import django_date_make_aware, string_to_date
from core.filters import generic_filtered_queryset
from question.models import MessagingQuestionStandard
from django.db.models import Count, Case, When, F


def get_messaging_question_per_origin_counts(
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
):
    
    queryset = MessagingQuestionStandard.objects.all()
    
    queryset = generic_filtered_queryset(
        queryset = queryset, 
        start_date = start_date, 
        end_date = end_date,
        origin_countries = origin_countries,
        destination_countries = destination_countries,
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
    ).order_by()
    
    origin_data = [count['count'] for count in origin_counts_data]
    origin_labels = [count['origin__name'].upper() for count in origin_counts_data if count['origin__name'] is not None]
    
    return {
            "data": origin_data,
            "labels": origin_labels,
        }


def get_messaging_question_per_destination_counts(
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
):  
     
    queryset = MessagingQuestionStandard.objects.all()
    
    
    queryset = generic_filtered_queryset(
        queryset = queryset, 
        start_date = start_date, 
        end_date = end_date,
        origin_countries = origin_countries,
        destination_countries = destination_countries,
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
    ).order_by()
    
    
    destination_data = [count['count'] for count in destination_counts_data]
    destination_labels = [count['destination__name'].upper() for count in destination_counts_data if count['destination__name'] is not None]
    
    return {
            "data": destination_data,
            "labels": destination_labels,
        }
    


def messaging_questions_count(
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
):
    
    queryset = MessagingQuestionStandard.objects.all()
    
    messaging_questions_count_queryset = generic_filtered_queryset(
        queryset = queryset, 
        start_date = start_date, 
        end_date = end_date,
        origin_countries = origin_countries,
        destination_countries = destination_countries,
    )
        
    return messaging_questions_count_queryset.count()