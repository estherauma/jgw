from datetime import datetime
from django.db.models import Q
from django.db.models import Count, F
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.helpers.preference_helpers.organisation import format_org_name_from_display
from common.inline import convert_question_key_to_readable_string, convert_to_camel_case
from common.utils.preferences import get_date_13_months_ago
from common.utils.strings import format_thousands_with_commas
from question.filters import question_response_filtered_queryset

from question.models import InlineQuestionResponse
from events.models import BigqueryHomepageEventData


def inline_questions_count(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_inline_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    else:
        base_queryset = InlineQuestionResponse.objects.all()
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    inline_questions_queryset = question_response_filtered_queryset(
        queryset=base_queryset, 
        **filters
    )

    return format_thousands_with_commas(inline_questions_queryset.count())


def get_inline_question_per_origin_counts(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_inline_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = InlineQuestionResponse.objects.all()

    inline_questions_queryset = question_response_filtered_queryset(
        queryset=base_queryset, 
        **filters
    )

    origin_counts_data = (
        inline_questions_queryset.annotate(origin_name=F("inline_question__inline_question_standard__origin__name"))
        .values("origin_name")
        .annotate(count=Count("origin_name"))
        .order_by("-count")
    )

    origin_data = [count["count"] for count in origin_counts_data]
    origin_labels = [
        count["origin_name"].title() for count in origin_counts_data if count["origin_name"] is not None
    ]

    return {
        "counts": origin_data,
        "labels": origin_labels,
    }


def get_inline_question_per_destination_counts(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_inline_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    else:
        base_queryset = InlineQuestionResponse.objects.all()
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    inline_questions_queryset = question_response_filtered_queryset(
        queryset=base_queryset, 
        **filters
    )

    destination_counts_data = (
        inline_questions_queryset.annotate(destination_name=F("inline_question__inline_question_standard__destination__name"))
        .values("destination_name")
        .annotate(count=Count("destination_name"))
        .order_by("-count")
    )

    destination_data = [count["count"] for count in destination_counts_data]
    destination_labels = [
        count["destination_name"].title()
        for count in destination_counts_data
        if count["destination_name"] is not None
    ]

    return {
        "counts": destination_data,
        "labels": destination_labels,
    }


def get_inline_question_per_organisation_counts(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_inline_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    else:
        base_queryset = InlineQuestionResponse.objects.all()
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    inline_questions_queryset = question_response_filtered_queryset(
        queryset=base_queryset, 
        **filters
    )
    organisation_counts_data = (
        inline_questions_queryset.annotate(
            organisation_name=F("inline_question__inline_question_standard__org_info__name")
        )
        .values("organisation_name")
        .annotate(count=Count("organisation_name"))
        .order_by("-count")
    )

    organisation_counts = [count["count"] for count in organisation_counts_data]
    organisation_labels = [
        organisation["organisation_name"]
        for organisation in organisation_counts_data
        if organisation["organisation_name"] is not None
    ]

    return {
        "counts": organisation_counts,
        "labels": organisation_labels,
    }


def get_inline_question_per_language_counts(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_inline_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    else:
        base_queryset = InlineQuestionResponse.objects.all()
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    inline_questions_queryset = question_response_filtered_queryset(
        queryset=base_queryset, 
        **filters
    )

    language_counts_data = (
        inline_questions_queryset.annotate(
            language_name=F("inline_question__inline_question_standard__language__translated_name"),
        )
        .values("language_name")
        .annotate(count=Count("language_name"))
        .order_by("-count")
    )

    language_counts = [count["count"] for count in language_counts_data]
    language_labels = [
        count["language_name"].title() for count in language_counts_data if count["language_name"] is not None
    ]

    return {
        "counts": language_counts,
        "labels": language_labels,
    }


def each_inline_question_response(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_inline_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    else:
        base_queryset = InlineQuestionResponse.objects.all()
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    inline_question_responses = question_response_filtered_queryset(
        queryset=base_queryset, **filters
    )
    inline_question_responses = inline_question_responses.exclude(response__translated_text="not specified")
    inline_questions_with_responses = inline_question_responses.values(
        "inline_question__question__translated_text",
        "inline_question__question__title_text",
        "response__translated_text",
    ).annotate(num_responses=Count("response__translated_text"))

    result_dict = {}
    for inline_questions_with_response in inline_questions_with_responses:
        title_text = inline_questions_with_response.get("inline_question__question__title_text")
        translated_text = inline_questions_with_response.get("inline_question__question__translated_text")
        response_text = inline_questions_with_response.get("response__translated_text")
        response_count = inline_questions_with_response.get("num_responses")

        if not title_text:
            title_text = convert_question_key_to_readable_string(translated_text)

        question_text = translated_text
        camel_case_question_text = convert_to_camel_case(question_text)
        question_in_result_dict = result_dict.get(camel_case_question_text)

        if question_in_result_dict:
            question_in_result_dict["labels"].append(response_text.capitalize())
            question_in_result_dict["counts"].append(response_count)
        else:
            result_dict[convert_to_camel_case(question_text)] = {
                "labels": [response_text.capitalize()],
                "counts": [response_count],
                "title": title_text,
            }

    return result_dict


def inline_question_responses_count(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_inline_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    else:
        base_queryset = InlineQuestionResponse.objects.all()
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    inline_questions_queryset = question_response_filtered_queryset(
        queryset=base_queryset, 
        **filters
    )
    inline_question_responses_count_queryset = inline_questions_queryset.count()

    return format_thousands_with_commas(inline_question_responses_count_queryset)


def inline_question_stats_for_export(filters):
    inline_question_per_origin = get_inline_question_per_origin_counts(**filters)
    inline_question_per_destination = get_inline_question_per_destination_counts(**filters)
    each_inline_question_response_data = each_inline_question_response(**filters)
    return {
        "responses_per_origin": inline_question_per_origin,
        "responses_per_destination": inline_question_per_destination,
        **each_inline_question_response_data,
    }


def inline_question_response():
    responses_count = (
        InlineQuestionResponse.objects.values(
            question_text=F("inline_question__question__text"), response_text=F("response__translated_text")
        )
        .annotate(response_count=Count("response"))
        .order_by("-response_count")
    )

    question_texts_list = []
    responses = []
    for response in responses_count:
        if response["question_text"] not in question_texts_list:
            question_texts_list.append(response["question_text"])
            responses.append(
                {
                    "response_texts": [response["response_text"]],
                    "response_counts": [response["response_count"]],
                }
            )
        else:
            responses[question_texts_list.index(response["question_text"])]["response_texts"].append(
                response["response_text"]
            )
            responses[question_texts_list.index(response["question_text"])]["response_counts"].append(
                response["response_count"]
            )

    return {"counts": responses, "labels": question_texts_list}


def get_all_inline_question_responses_data(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_inline_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )
        base_queryset = base_queryset.exclude(response__translated_text="not specified")
    else:
        base_queryset = InlineQuestionResponse.objects.all()
        base_queryset = base_queryset.exclude(response__translated_text="not specified")

    responses = (
        question_response_filtered_queryset(queryset=base_queryset, **filters)
        .exclude(Q(inline_question__question__text="not specified"))
        .select_related(
            "inline_question__inline_question_standard",
            "inline_question__question",
            "inline_question__inline_question_standard__api_created_at",
            "inline_question__inline_question_standard__api_updated_at",
            "inline_question__inline_question_standard__route",
            "inline_question__inline_question_standard__language",
            "inline_question__inline_question_standard__origin",
            "inline_question__inline_question_standard__destination",
            "inline_question__inline_question_standard__organisation_sector",
            "inline_question__inline_question_standard__org_info",
        )
        .values(
            "inline_question__inline_question_standard__device_id",
            "inline_question__inline_question_standard__api_created_at",
            "inline_question__inline_question_standard__api_updated_at",
            "inline_question__inline_question_standard__language__name",
            "inline_question__inline_question_standard__origin__name",
            "inline_question__inline_question_standard__destination__name",
            "inline_question__inline_question_standard__organisation_sector__name",
            "inline_question__inline_question_standard__org_info__name",
            "inline_question__inline_question_standard__route__name",
            "inline_question__question__text",
            "inline_question__question__title_text",
            "response__translated_text",
        )
    )

    data = []
    for response in responses:
        data.append(
            {
                "device_id": response["inline_question__inline_question_standard__device_id"],
                "created_at": response["inline_question__inline_question_standard__api_created_at"].strftime(
                    "%Y-%m-%d"
                ),
                "updated_at": response["inline_question__inline_question_standard__api_updated_at"].strftime(
                    "%Y-%m-%d"
                ),
                "language": response["inline_question__inline_question_standard__language__name"],
                "origin": response["inline_question__inline_question_standard__origin__name"],
                "destination": response["inline_question__inline_question_standard__destination__name"],
                "organisation_sector": response[
                    "inline_question__inline_question_standard__organisation_sector__name"
                ],
                "organisation": response["inline_question__inline_question_standard__org_info__name"],
                "route": response["inline_question__inline_question_standard__route__name"],
                "question_key": response["inline_question__question__text"],
                "title_text": response["inline_question__question__title_text"],
                "response": response["response__translated_text"],
            }
        )

    return data


def get_inline_questions_by_homepage_events(start_date=None, end_date=None):
    """
    Retrieves inline questions for users who have homepage events within the specified date range.
    
    Args:
        start_date (date, optional): Start date for filtering homepage events
        end_date (date, optional): End date for filtering homepage events
        
    Returns:
        QuerySet: InlineQuestionResponse queryset filtered by device_ids from homepage events
    """
    if start_date is None:
        start_date = get_date_13_months_ago()
    if end_date is None:
        end_date = datetime.now().date()

    homepage_events = BigqueryHomepageEventData.objects.filter(
        Q(event_date__range=(start_date, end_date))
    )

    device_ids = homepage_events.values_list('device_id', flat=True).distinct()

    inline_questions = InlineQuestionResponse.objects.filter(
        inline_question__inline_question_standard__device_id__in=device_ids
    )

    return inline_questions
