from common.utils.strings import format_thousands_with_commas
from datetime import datetime
from question.filters import generic_question_filtered_queryset
from question.models import InlineQuestionResponse, InlineQuestionResponseText, MessagingQuestionResponse, MessagingQuestionStandard
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

def get_all_messaging_question_responses_data(start_date, end_date):
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

    responses = MessagingQuestionResponse.objects.filter(
        messaging_question__messaging_question_standard__api_created_at__range=(start_date_obj, end_date_obj)
    ).select_related(
        'messaging_question__messaging_question_standard', 
        'messaging_question__question', 
        'messaging_question__messaging_question_standard__route',
        'messaging_question__messaging_question_standard__language',
        'messaging_question__messaging_question_standard__origin',
        'messaging_question__messaging_question_standard__destination',
        'messaging_question__messaging_question_standard__organisation_sector',
        'messaging_question__messaging_question_standard__factory_farm',
        'messaging_question__messaging_question_standard__organisation'
    ).prefetch_related(
        'responses__option'
    )

    data = []
    for response in responses:
        if response.messaging_question is None:
            continue
        standard = response.messaging_question.messaging_question_standard
        question_text = response.messaging_question.question.translated_text if response.messaging_question.question else None
        if not question_text:
            continue
        response_texts = [res.option.translated_option for res in response.responses.all()]

        data.append({
            'api_created_at': standard.api_created_at,
            'api_updated_at': standard.api_updated_at,
            'data_source_id': standard.data_source_id,
            'device_id': standard.device_id,
            'app_id': standard.app_id,
            'locale': standard.locale,
            'route': standard.route,
            'language': standard.language,
            'origin': standard.origin,
            'destination': standard.destination,
            'organisation_sector': standard.organisation_sector,
            'factory_farm': standard.factory_farm,
            'organisation': standard.organisation,
            'question': question_text,
            'responses': response_texts,
        })
    return data
