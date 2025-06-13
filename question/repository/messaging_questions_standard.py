from collections import defaultdict
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.utils.preferences import get_date_13_months_ago
from common.utils.strings import format_thousands_with_commas
from events.models import BigqueryHomepageEventData
from question.filters import generic_question_filtered_queryset, message_data_sent_filtered_queryset
from question.models import MessageDataSent, MessagingQuestionResponse, MessagingQuestionStandard
from django.db.models import Count, Case, When, F, Q
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime


def get_messaging_question_per_origin_counts(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_messaging_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = MessagingQuestionStandard.objects.all()

    queryset = generic_question_filtered_queryset(queryset=base_queryset, **filters)

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
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_messaging_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = MessagingQuestionStandard.objects.all()

    queryset = generic_question_filtered_queryset(queryset=base_queryset, **filters)

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
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_messaging_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = MessagingQuestionStandard.objects.all()

    messaging_questions_count_queryset = generic_question_filtered_queryset(
        queryset=base_queryset, **filters
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

    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_messaging_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = MessagingQuestionStandard.objects.all()

    messaging_question_standards = generic_question_filtered_queryset(
        queryset=base_queryset, **filters
    )

    test_patterns = ["test 2 q", "testq", "test qn", "question"]
    exclude_q = Q()
    for pattern in test_patterns:
        exclude_q |= Q(messaging_question__question__text__icontains=pattern)
    messaging_question_responses = (
        MessagingQuestionResponse.objects.filter(
            messaging_question__messaging_question_standard__in=messaging_question_standards
        )
        .exclude(responses__option__translated_option__iexact="not specified")
        .values(
            "messaging_question__question__translated_text",
            "messaging_question__question__text",
            "responses__option__translated_option",
        )
        .annotate(num_responses=Count("responses__option__translated_option"))
        .order_by("-num_responses")
    )

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
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_messaging_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = MessagingQuestionStandard.objects.all()

    queryset = generic_question_filtered_queryset(queryset=base_queryset, **filters)
    queryset = (
        queryset
        .select_related(
            "language", "origin", "destination", "organisation_sector", "factory_farm", "organisation"
        )
        .prefetch_related(
            "question_standard", "question_standard__messagingquestionresponse_set__responses__option"
        )
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

            data.append(
                {
                    "api_created_at": standard.api_created_at,
                    "api_updated_at": standard.api_updated_at,
                    "message_id": standard.message_id,
                    "data_source_id": standard.data_source_id,
                    "device_id": standard.device_id,
                    "app_id": standard.app_id,
                    "locale": standard.locale,
                    "language": standard.language.name if standard.language else None,
                    "origin": standard.origin.name if standard.origin else None,
                    "destination": standard.destination.name if standard.destination else None,
                    "organisation_sector": (
                        standard.organisation_sector.name if standard.organisation_sector else None
                    ),
                    "factory_farm": standard.factory_farm.name if standard.factory_farm else None,
                    "organisation": standard.organisation.name if standard.organisation else None,
                    "question": question_text,
                    "response": response_text,
                    "translated_response": translated_response_text,
                }
            )

    return data


def get_messaging_question_per_organisation_counts(**filters):
    """
    Retrieves the count of messaging question responses per organization.

    This function filters messaging question responses based on the provided filters,
    excludes responses with "not specified" options, and aggregates the count for each organization.

    Args:
        **filters: Arbitrary keyword arguments for filtering the queryset.

    Returns:
        dict: A dictionary containing two keys:
            - "counts": A list of response counts for each organization.
            - "labels": A list of organization names (capitalized) corresponding to the counts.

    Raises:
        ObjectDoesNotExist: If no matching objects are found.
        Exception: For any other unexpected errors during execution.
    """
    try:
        show_new_user_data = filters.get('show_new_user_data', False)
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')

        if show_new_user_data is False:
            base_queryset = get_messaging_questions_by_homepage_events(
                start_date=start_date,
                end_date=end_date
            )

        else:
            base_queryset = MessagingQuestionStandard.objects.all()

        queryset = generic_question_filtered_queryset(queryset=base_queryset, **filters)

        organisation_counts_data = (
            queryset
            .values(
                org_info__name=F("org_info__name")
            )
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )

        organisation_data = [count["count"] for count in organisation_counts_data]
        organisation_labels = [
            count["org_info__name"].title()
            for count in organisation_counts_data
            if count["org_info__name"] is not None
        ]

        return {
            "counts": organisation_data,
            "labels": organisation_labels,
        }

    except ObjectDoesNotExist:
        return {
            "counts": [],
            "labels": [],
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "counts": [],
            "labels": [],
        }


def get_all_message_data_sent(**filters):
    """
    Get all message data sent with applied filters
    """
    queryset = message_data_sent_filtered_queryset(
        queryset=MessageDataSent.objects.select_related("language", "destination", "organisation", "message_content"), **filters
    )

    data = []
    for message in queryset:
        data.append(
            {
                "api_created_at": message.api_created_at,
                "api_updated_at": message.api_updated_at,
                "message_id": message.message_id,
                "device_id": message.device_id,
                "language": message.language.name if message.language else None,
                "destination": message.destination.name if message.destination else None,
                "message_title": message.message_title,
                "message_title_english": message.message_title_english,
                "actual_message": message.message_content.message if message.message_content else None,
                "message_date": message.message_date,
                "message_delivered": message.message_delivered,
                "message_queued": message.message_queued,
                "message_notification_sent_to_FCM": message.message_notification_sent_to_fcm,
                "message_delivered_date": message.message_delivered_date,
                "organisation": message.organisation.name if message.organisation else None,
            }
        )

    return data


def get_messaging_questions_by_homepage_events(start_date=None, end_date=None):
    """
    Retrieves messaging questions for users who have homepage events within the specified date range.
    
    Args:
        start_date (date, optional): Start date for filtering homepage events
        end_date (date, optional): End date for filtering homepage events
        
    Returns:
        QuerySet: MessagingQuestionResponse queryset filtered by device_ids from homepage events
    """
    if start_date is None:
        start_date = get_date_13_months_ago()
    if end_date is None:
        end_date = datetime.now().date()

    homepage_events = BigqueryHomepageEventData.objects.filter(
        Q(event_date__range=(start_date, end_date))
    )

    device_ids = homepage_events.values_list('device_id', flat=True).distinct()

    messaging_questions = MessagingQuestionStandard.objects.filter(
        device_id__in=device_ids
    )

    return messaging_questions


def get_messaging_question_by_age(**filters):
    """
    Retrieves the count of messaging question responses broken down by age ranges.

    Args:
        **filters: Arbitrary keyword arguments for filtering the queryset.

    Returns:
        dict: A dictionary containing:
            - "labels": List of age ranges
            - "counts": List of counts for each age range
    """
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_messaging_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )
    else:
        base_queryset = MessagingQuestionStandard.objects.all()

    queryset = generic_question_filtered_queryset(queryset=base_queryset, **filters)

    age_counts = (
        queryset
        .values('preference__age__translated_range')
        .annotate(count=Count('id'))
        .order_by('preference__age__translated_range')
    )

    age_ranges = {
        '18-20': 0,
        '21-30': 0,
        '31-40': 0,
        '41-50': 0,
        '51-60': 0,
        'Prefer not to answer': 0
    }

    for age_count in age_counts:
        age_range = age_count['preference__age__translated_range']
        count = age_count['count']
        
        if age_range is None:
            continue
            
        if age_range.lower() in ['prefer not to answer', 'prefernottoanswer']:
            age_ranges['Prefer not to answer'] += count
        elif age_range in age_ranges:
            age_ranges[age_range] += count

    age_ranges = {k: v for k, v in age_ranges.items() if v > 0}

    return {
        'labels': list(age_ranges.keys()),
        'counts': list(age_ranges.values())
    }


def get_messaging_question_by_gender(**filters):
    """
    Retrieves the count of messaging question responses broken down by gender.

    Args:
        **filters: Arbitrary keyword arguments for filtering the queryset.

    Returns:
        dict: A dictionary containing:
            - "labels": List of gender categories
            - "counts": List of counts for each gender category
    """
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_messaging_questions_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )
    else:
        base_queryset = MessagingQuestionStandard.objects.all()

    queryset = generic_question_filtered_queryset(queryset=base_queryset, **filters)

    gender_counts = (
        queryset
        .values('preference__gender__name')
        .annotate(count=Count('id'))
        .order_by('preference__gender__name')
    )

    gender_data = {
        'Male': 0,
        'Female': 0,
        'Prefer not to answer': 0
    }

    for gender_count in gender_counts:
        gender = gender_count['preference__gender__name']
        count = gender_count['count']
        
        if gender is None:
            continue
            
        if gender.lower() == 'male':
            gender_data['Male'] += count
        elif gender.lower() == 'female':
            gender_data['Female'] += count
        else:
            gender_data['Prefer not to answer'] += count

    return {
        'labels': list(gender_data.keys()),
        'counts': list(gender_data.values())
    }
