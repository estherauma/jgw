from django.db.models import Count, Case, When, F
from common.helpers.preference_helpers.organisation import format_org_name_from_display

from core.filters import generic_filtered_queryset
from question.models import InlineQuestionStandard


def inline_questions_count(**filters):
    
    inline_questions_count_queryset = generic_filtered_queryset(
        queryset = InlineQuestionStandard.objects.all(), 
        **filters
    )
        
    return inline_questions_count_queryset.count()


def get_inline_question_per_origin_counts(**filters):
    
    queryset = generic_filtered_queryset(
        queryset = InlineQuestionStandard.objects.all(), 
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
    ).order_by()
    
    origin_data = [count['count'] for count in origin_counts_data]
    origin_labels = [count['origin__name'].upper() for count in origin_counts_data if count['origin__name'] is not None]
    
    return {
            "counts": origin_data,
            "labels": origin_labels,
        }


def get_inline_question_per_destination_counts(**filters):  
        
    queryset = generic_filtered_queryset(
        queryset = InlineQuestionStandard.objects.all(), 
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
    ).order_by()
    
    
    destination_data = [count['count'] for count in destination_counts_data]
    destination_labels = [count['destination__name'].upper() for count in destination_counts_data if count['destination__name'] is not None]
    
    return {
            "counts": destination_data,
            "labels": destination_labels,
        }
    
    
def get_inline_question_per_organisation_counts(**filters):
    
    queryset = generic_filtered_queryset(
        queryset = InlineQuestionStandard.objects.all(), 
        **filters
    )
        
    organisation_counts_data = queryset.annotate(
        origin_name=Case(
            When(preference__isnull=False, then=F('preference__organisation__name')),
            default=F('organisation__name')
        )
    ).values(
        'organisation__name'
    ).annotate(
        count=Count('organisation__name')
    ).order_by()
    
    organisation_counts = [count['count'] for count in organisation_counts_data]
    organisation_labels = [format_org_name_from_display(organisation['organisation__name']).upper() for organisation in organisation_counts_data]
    
    return {
            "counts": organisation_counts,
            "labels": organisation_labels,
        }
    
    
def get_inline_question_per_language_counts(**filters):
    
    queryset = generic_filtered_queryset(
        queryset = InlineQuestionStandard.objects.all(), 
        **filters
    )
        
    language_counts_data = queryset.annotate(
        origin_name=Case(
            When(preference__isnull=False, then=F('preference__language__translated_name')),
            default=F('language__translated_name')
        )
    ).values(
        'language__translated_name'
    ).annotate(
        count=Count('language__translated_name')
    ).order_by()
    
    language_counts = [count['count'] for count in language_counts_data]
    language_labels = [count['language__translated_name'].upper() for count in language_counts_data if count['language__translated_name'] is not None]
    
    return {
            "counts": language_counts,
            "labels": language_labels,
        }