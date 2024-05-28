from django.db.models import Count, Case, When, F
from common.helpers.preference_helpers.organisation import format_org_name_from_display
from common.inline import convert_question_key_to_readable_string
from common.utils.strings import format_thousands_with_commas
from question.filters import generic_question_filtered_queryset, question_response_filtered_queryset

from question.models import InlineQuestionResponse, InlineQuestionStandard


def inline_questions_count(**filters):
    inline_questions_count_queryset = generic_question_filtered_queryset(
        queryset=InlineQuestionStandard.objects.all(), **filters
    )

    return format_thousands_with_commas(inline_questions_count_queryset.count())


def get_inline_question_per_origin_counts(**filters):
    queryset = question_response_filtered_queryset(
        queryset=InlineQuestionResponse.objects.all(), **filters
    )
    queryset = queryset.exclude(response__translated_text="not specified")

    origin_counts_data = (
        queryset.annotate(
            origin_name=Case(
                When(inline_question__inline_question_standard__preference__isnull=False, 
                     then=F("inline_question__inline_question_standard__preference__origin__name")),
                default=F("inline_question__inline_question_standard__origin__name")
            )
        )
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
    queryset = question_response_filtered_queryset(
        queryset=InlineQuestionResponse.objects.all(), **filters
    )
    queryset = queryset.exclude(response__translated_text="not specified")
    
    destination_counts_data = (
        queryset.annotate(
            destination_name=F("inline_question__inline_question_standard__destination__name")
        )
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
    queryset = question_response_filtered_queryset(
        queryset=InlineQuestionResponse.objects.all(), **filters
    )
    queryset = queryset.exclude(response__translated_text="not specified")
    
    organisation_counts_data = (
        queryset.annotate(
            organisation_name=F("inline_question__inline_question_standard__organisation__name")
        )
        .values("organisation_name")
        .annotate(count=Count("organisation_name"))
        .order_by("-count")
    )

    organisation_counts = [count["count"] for count in organisation_counts_data]
    organisation_labels = [
        format_org_name_from_display(organisation["organisation_name"]).title()
        for organisation in organisation_counts_data
    ]

    return {
        "counts": organisation_counts,
        "labels": organisation_labels,
    }


from django.db.models import Case, Count, F, When

def get_inline_question_per_language_counts(**filters):
    queryset = question_response_filtered_queryset(
        queryset=InlineQuestionResponse.objects.all(), **filters
    )
    queryset = queryset.exclude(response__translated_text="not specified")

    language_counts_data = (
        queryset.annotate(
            language_name=F("inline_question__inline_question_standard__language__translated_name"),
            )
        .values("language_name")
        .annotate(count=Count("language_name"))
        .order_by("-count")
    )

    language_counts = [count["count"] for count in language_counts_data]
    language_labels = [
        count["language_name"].title()
        for count in language_counts_data
        if count["language_name"] is not None
    ]

    return {
        "counts": language_counts,
        "labels": language_labels,
    }


def each_inline_question_response(**filters):
    inline_question_responses = question_response_filtered_queryset(
        queryset=InlineQuestionResponse.objects.all(), **filters
    )
    inline_question_responses = inline_question_responses.exclude(response__translated_text="not specified")
    inline_questions_with_responses = inline_question_responses.values(
        "inline_question__question__translated_text","inline_question__question__title_text", "response__translated_text"
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

        question_in_result_dict = result_dict.get(question_text)

        if question_in_result_dict:
            question_in_result_dict.get("labels").append(response_text.capitalize())
            question_in_result_dict.get("counts").append(response_count)
        else:
            result_dict[question_text] = {"labels": [response_text.capitalize()], "counts": [response_count],"title":title_text}
    
    return result_dict


def inline_question_responses_count(**filters):
    inline_question_responses = question_response_filtered_queryset(
        queryset=InlineQuestionResponse.objects.all(), **filters
    )
    inline_question_responses_filtered = inline_question_responses.exclude(response__translated_text="not specified")
    inline_question_responses_count_queryset = inline_question_responses_filtered.count()

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
