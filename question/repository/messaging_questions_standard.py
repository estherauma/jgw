from collections import defaultdict
from common.utils.strings import format_thousands_with_commas
from question.filters import generic_question_filtered_queryset
from question.models import MessagingQuestionResponse, MessagingQuestionStandard
from django.db.models import Count, Case, When, F


def get_messaging_question_per_origin_counts(**filters):
    queryset = generic_question_filtered_queryset(queryset=MessagingQuestionStandard.objects.all(), **filters)

    origin_counts_data = (
        queryset.annotate(
            origin_name=Case(
                When(preference__isnull=False, then=F("preference__origin__name")), default=F("origin__name")
            )
        )
        .values("origin__name")
        .annotate(count=Count("origin__name"))
        .order_by("-count")
    )

    origin_data = [count["count"] for count in origin_counts_data]
    origin_labels = [
        count["origin__name"].title() for count in origin_counts_data if count["origin__name"] is not None
    ]

    return {
        "counts": origin_data,
        "labels": origin_labels,
    }


def get_messaging_question_per_destination_counts(**filters):
    queryset = generic_question_filtered_queryset(queryset=MessagingQuestionStandard.objects.all(), **filters)
    destination_counts_data = (
        queryset.annotate(
            destination_name=Case(
                When(preference__isnull=False, then=F("preference__destination__name")),
                default=F("destination__name"),
            )
        )
        .values("destination__name")
        .annotate(count=Count("destination__name"))
        .order_by("-count")
    )

    destination_data = [count["count"] for count in destination_counts_data]
    destination_labels = [
        count["destination__name"].title()
        for count in destination_counts_data
        if count["destination__name"] is not None
    ]

    return {
        "counts": destination_data,
        "labels": destination_labels,
    }


def messaging_questions_count(**filters):
    messaging_questions_count_queryset = generic_question_filtered_queryset(
        queryset=MessagingQuestionStandard.objects.all(), **filters
    )

    return format_thousands_with_commas(messaging_questions_count_queryset.count())


def messaging_question_stats_for_export(filters):
    messaging_question_per_origin = get_messaging_question_per_origin_counts(**filters)
    messaging_question_per_destination = get_messaging_question_per_destination_counts(**filters)
    return {
        "responses_per_origin": messaging_question_per_origin,
        "responses_per_destination": messaging_question_per_destination,
    }

def each_messaging_question_response(**filters):
    """
    Fetches and aggregates responses for messaging questions, applying specified filters.
    
    Args:
        **filters: Keyword arguments used to filter the messaging questions.

    Returns:
        dict: A dictionary where keys are question texts (translated), and values contain:
            - 'labels': List of response options.
            - 'counts': List of counts for each response option.
            - 'title': Original or translated text of the question.
    """
  
    messaging_question_standards = generic_question_filtered_queryset(
        queryset=MessagingQuestionStandard.objects.all(),
        **filters
    )

    messaging_question_responses = MessagingQuestionResponse.objects.filter(
        messaging_question__messaging_question_standard__in=messaging_question_standards
    ).exclude(
        responses__option__translated_option__iexact="not specified" 
    ).values(
        "messaging_question__question__translated_text",
        "messaging_question__question__text",
        "responses__option__translated_option"
    ).annotate(
        num_responses=Count("responses__option__translated_option")
    ).order_by("-num_responses")

    result_dict = {}
    
    for response in messaging_question_responses:
        question_text = response.get("messaging_question__question__translated_text")
        response_text = response.get("responses__option__translated_option")
        response_count = response.get("num_responses")

        result_dict = defaultdict(lambda: {"labels": [], "counts": [], "title": ""})

        for response in messaging_question_responses:
            question_text = response.get("messaging_question__question__translated_text")
            response_text = response.get("responses__option__translated_option")
            response_count = response.get("num_responses")

            if question_text and response_text is not None:
                result_dict[question_text]["labels"].append(response_text)
                result_dict[question_text]["counts"].append(response_count)
                result_dict[question_text]["title"] = question_text

        return dict(result_dict)

def get_all_messaging_question_responses_data(**filters):
    queryset = generic_question_filtered_queryset(queryset=MessagingQuestionStandard.objects.all(), **filters).select_related(
     'language', 'origin', 'destination', 'organisation_sector', 'factory_farm', 'organisation'
    ).prefetch_related(
        'question_standard',
        'question_standard__messagingquestionresponse_set__responses__option' 
    )

    data = []
    for standard in queryset:
        for messaging_question in standard.question_standard.all():
            if not messaging_question.question:
                continue
            question_text = messaging_question.question.translated_text
            responses = []
            for response in messaging_question.messagingquestionresponse_set.all():
                for option in response.responses.all():
                    response_text = option.option.option
                    translated_response_text = option.option.translated_option
                    responses.append(response_text)
            if not question_text:
                continue
            
            data.append({
                'api_created_at': standard.api_created_at,
                'api_updated_at': standard.api_updated_at,
                'message_id': standard.message_id,
                'data_source_id': standard.data_source_id,
                'device_id': standard.device_id,
                'app_id': standard.app_id,
                'locale': standard.locale,
                'language': standard.language.name if standard.language else None,
                'origin': standard.origin.name if standard.origin else None,
                'destination': standard.destination.name if standard.destination else None,
                'organisation_sector': standard.organisation_sector.name if standard.organisation_sector else None,
                'factory_farm': standard.factory_farm.name if standard.factory_farm else None,
                'organisation': standard.organisation.name if standard.organisation else None,
                'question': question_text,
                'response': response_text,
                'translated_response': translated_response_text,
            })

    return data
