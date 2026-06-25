"""Build User Insights indicator breakdown panels from lead response tables."""

import re
from collections import Counter, defaultdict
from datetime import date, datetime

from django.db.models import Prefetch
from django.utils.formats import date_format
from django.utils.translation import gettext as _

from question.filters import (
    lead_inline_question_response_filtered_queryset,
    lead_messaging_question_response_filtered_queryset,
)
from question.models import (
    FollowupFollowupInlineQuestionResponse,
    FollowupFollowupMessagingQuestionResponse,
    FollowupInlineQuestionResponse,
    FollowupMessagingQuestionResponse,
    LeadInlineQuestionResponse,
    LeadMessagingQuestionResponse,
    UniqueInlineQuestion,
    UniqueMessagingQuestion,
)

OPEN_TEXT_RESPONSE_TYPES = frozenset({"text", "open_text", "textarea"})
QUESTION_TEXT_STOP_WORDS = frozenset({
    "a", "an", "and", "any", "are", "been", "did", "do", "does", "for", "have",
    "how", "in", "is", "of", "on", "or", "the", "to", "was", "were", "what",
    "when", "where", "who", "you", "your",
})
SUNBURST_COLOR_YES = "#9e1b32"
SUNBURST_COLOR_NO = "#5a6a7d"
SUNBURST_FOLLOW_UP_COLORS = ("#7a1530", "#a82845", "#b8324f", "#c43d59", "#d04863")
SUNBURST_FOLLOW_UP_FF_COLORS = ("#e8a4b8", "#f0c4d0", "#f5d5de", "#f8dee6")


def _slugify(value, prefix=""):
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "unknown").lower()).strip("-")[:80]
    return f"{prefix}-{slug}" if prefix else slug


def _token_set(text):
    tokens = set(re.findall(r"[a-z0-9]+", (text or "").lower()))
    return {token for token in tokens if token not in QUESTION_TEXT_STOP_WORDS and len(token) > 1}


def _related_question_keys(question_key, question_text, catalog, *, min_overlap=0.55):
    """
    Include catalog keys whose question text closely matches the configured lead question.

    Follow-up rows are often stored against legacy/alternate question_key variants
    (e.g. recruiterKeptId vs asvRecruiterKeptId) that share the same wording.
    """
    keys = {question_key}
    base_tokens = _token_set(question_text)
    if len(base_tokens) < 2:
        return keys

    for entry in catalog:
        if entry.question_key == question_key:
            continue
        other_tokens = _token_set(entry.question_text)
        if len(other_tokens) < 2:
            continue
        overlap = len(base_tokens & other_tokens) / len(base_tokens | other_tokens)
        if overlap >= min_overlap:
            keys.add(entry.question_key)
    return keys


def _sunburst_color_for_option(option_index, total_options, depth):
    if depth <= 1:
        palette = SUNBURST_FOLLOW_UP_COLORS
    else:
        palette = SUNBURST_FOLLOW_UP_FF_COLORS
    if total_options <= 1:
        return palette[min(depth - 1, len(palette) - 1)]
    palette_index = min(
        int(option_index * len(palette) / total_options),
        len(palette) - 1,
    )
    return palette[palette_index]


def _build_sunburst_from_follow_up(follow_up, depth=1):
    options = follow_up.get("options") or []
    nodes = []
    for index, option in enumerate(options):
        node = {
            "name": option["label"],
            "value": option["count"],
            "question": follow_up.get("text") or "",
            "itemStyle": {
                "color": _sunburst_color_for_option(index, len(options), depth),
            },
        }
        nested = option.get("follow_up")
        if nested:
            node["children"] = _build_sunburst_from_follow_up(nested, depth=depth + 1)
        nodes.append(node)
    return nodes


def _build_sunburst_from_responses(lead_text, responses):
    """Build ECharts sunburst payload from nested lead/follow-up response data."""
    nodes = []
    for response in responses:
        label = (response.get("label") or "").strip().lower()
        is_yes = response.get("id") == "yes" or label in {"yes", "true"}
        node = {
            "name": response["label"],
            "value": response["count"],
            "question": lead_text,
            "itemStyle": {"color": SUNBURST_COLOR_YES if is_yes else SUNBURST_COLOR_NO},
        }
        follow_up = response.get("follow_up")
        if follow_up:
            node["children"] = _build_sunburst_from_follow_up(follow_up, depth=1)
        nodes.append(node)
    return nodes


def _responses_have_follow_up(responses):
    return any(response.get("follow_up") for response in responses or [])


def _pick_expanded_lead_question(lead_questions):
    for question in lead_questions:
        if question.get("response_type") == "choice" and _responses_have_follow_up(
            question.get("responses")
        ):
            return question
    for question in lead_questions:
        if question.get("total"):
            return question
    return lead_questions[0] if lead_questions else None


def _lead_question_has_filtered_responses(lead_question):
    """True when the question has at least one in-scope response after dashboard filters."""
    if lead_question.get("response_type") == "open_text":
        return lead_question.get("text_detail", {}).get("total_count", 0) > 0
    return lead_question.get("total", 0) > 0


def _response_date(row):
    return getattr(row, "question_response_date", None) or getattr(row, "api_created_at", None)


def _format_date(value):
    if not value:
        return ""
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return date_format(value, "SHORT_DATE_FORMAT")
    return str(value)


def _label_fn_for_channel(channel):
    return _inline_answer_label if channel == "inline" else _messaging_answer_label


def _inline_answer_label(row):
    if row.inline_question_response:
        for candidate in (
            row.inline_question_response.response_text,
            row.inline_question_response.response_key,
        ):
            if candidate and str(candidate).strip():
                return str(candidate).strip()
    if row.response_value and str(row.response_value).strip():
        return str(row.response_value).strip()
    return "—"


def _messaging_answer_label(row):
    if row.messaging_question_response:
        for candidate in (
            row.messaging_question_response.response_text,
            row.messaging_question_response.response_key,
        ):
            if candidate and str(candidate).strip():
                return str(candidate).strip()
    if row.response_value and str(row.response_value).strip():
        return str(row.response_value).strip()
    return "—"


def _inline_native_text(row):
    if row.inline_question_response and row.inline_question_response.response_text:
        return str(row.inline_question_response.response_text).strip()
    if row.response_value and str(row.response_value).strip():
        return str(row.response_value).strip()
    return ""


def _messaging_native_text(row):
    if row.messaging_question_response and row.messaging_question_response.response_text:
        return str(row.messaging_question_response.response_text).strip()
    if row.response_value and str(row.response_value).strip():
        return str(row.response_value).strip()
    return ""


def _translation_text(row, channel, na_label):
    if channel == "inline":
        translated = (
            row.inline_question_response.response_text_translated
            if row.inline_question_response
            else None
        )
    else:
        translated = (
            row.messaging_question_response.response_text_translated
            if row.messaging_question_response
            else None
        )
    if translated and str(translated).strip():
        return str(translated).strip()
    return na_label


def _is_open_text_row(row):
    return (row.questionresponsetype or "").lower() in OPEN_TEXT_RESPONSE_TYPES


def _question_text_from_row(row, channel):
    if channel == "inline":
        if row.inline_question_id and row.inline_question.question_text:
            return row.inline_question.question_text
        if row.inline_question_id and row.inline_question.question_key:
            return row.inline_question.question_key
    else:
        if row.messaging_question_id and row.messaging_question.question_text:
            return row.messaging_question.question_text
        if row.messaging_question_id and row.messaging_question.question_key:
            return row.messaging_question.question_key
    return "Follow-up question"


def _group_rows_by_question_key(rows, channel):
    grouped = defaultdict(list)
    for row in rows:
        if channel == "inline":
            key = (
                row.inline_question.question_key
                if row.inline_question_id and row.inline_question.question_key
                else str(row.pk)
            )
        else:
            key = (
                row.messaging_question.question_key
                if row.messaging_question_id and row.messaging_question.question_key
                else str(row.pk)
            )
        grouped[key].append(row)
    return grouped


def _apply_default_drilldown_selection(responses):
    """
    Select the first answer branch that has follow-ups (and each nested branch),
    so follow-up questions are visible when a lead question is expanded.
    """
    if not responses:
        return []

    crumbs = []
    response = next((item for item in responses if item.get("follow_up")), None)
    if not response:
        return crumbs

    response["selected"] = True
    crumbs.append(response["label"])

    follow_up = response.get("follow_up")
    while follow_up and follow_up.get("options"):
        options = follow_up["options"]
        option = next((item for item in options if item.get("follow_up")), options[0])
        option["selected"] = True
        crumbs.append(option["label"])
        follow_up = option.get("follow_up")

    return crumbs


def _follow_up_code(question_number, depth):
    letter = chr(ord("A") + depth - 1)
    return f"{question_number}{letter}"


def _build_follow_up_tree(followup_rows, channel, question_number, depth=1):
    """Build nested follow-up payload (options may contain deeper follow_up)."""
    if not followup_rows:
        return None

    label_fn = _label_fn_for_channel(channel)
    by_question = _group_rows_by_question_key(followup_rows, channel)
    _, qrows = max(by_question.items(), key=lambda item: len(item[1]))
    total = len(qrows)

    options = []
    rows_by_answer = defaultdict(list)
    for row in qrows:
        rows_by_answer[label_fn(row)].append(row)

    for answer_label, count in Counter(label_fn(row) for row in qrows).most_common():
        option = {
            "id": _slugify(answer_label),
            "label": answer_label,
            "count": count,
            "total": total,
            "selected": False,
        }
        child_rows = []
        if depth < 2:
            for parent in rows_by_answer[answer_label]:
                child_rows.extend(list(parent.followup_followup_responses.all()))
        nested = _build_follow_up_tree(
            child_rows, channel, question_number, depth=depth + 1
        )
        if nested:
            option["follow_up"] = nested
        options.append(option)

    return {
        "code": _follow_up_code(question_number, depth),
        "text": _question_text_from_row(qrows[0], channel),
        "options": options,
    }


def _choice_responses_with_followups(lead_rows, channel, question_number):
    """Aggregate lead answers and attach follow-up / follow-up-of-follow-up trees."""
    if not lead_rows:
        return [], 0

    label_fn = _label_fn_for_channel(channel)
    total = len(lead_rows)
    lead_ids = [row.pk for row in lead_rows]

    if channel == "inline":
        followups = _fetch_inline_followups(lead_ids)
    else:
        followups = _fetch_messaging_followups(lead_ids)

    followups_by_lead = defaultdict(list)
    for row in followups:
        followups_by_lead[row.lead_question_id].append(row)

    rows_by_answer = defaultdict(list)
    for row in lead_rows:
        rows_by_answer[label_fn(row)].append(row)

    responses = []
    for answer_label, count in Counter(label_fn(row) for row in lead_rows).most_common():
        option = {
            "id": _slugify(answer_label),
            "label": answer_label,
            "count": count,
            "total": total,
            "selected": False,
        }
        followup_rows = []
        for lead in rows_by_answer[answer_label]:
            followup_rows.extend(followups_by_lead.get(lead.pk, []))
        follow_up = _build_follow_up_tree(
            followup_rows, channel, question_number, depth=1
        )
        if follow_up:
            option["follow_up"] = follow_up
        responses.append(option)

    return responses, total


def _text_detail_for_rows(rows, channel, question_label, indicator_name, na_label):
    table_rows = []
    preview = []
    for row in rows:
        native = (
            _inline_native_text(row) if channel == "inline" else _messaging_native_text(row)
        )
        if not native:
            continue
        response_id = row.data_source_id or str(row.pk)
        translation = _translation_text(row, channel, na_label)
        entry = {
            "date": _format_date(_response_date(row)),
            "id": response_id,
            "label": f"#{response_id}",
            "native": native,
            "translation": translation,
            "starred": False,
        }
        table_rows.append(entry)
        if len(preview) < 10:
            preview.append(entry)

    text_crumb = str(_("userInsightsMockTextResponseCrumb")) % {"question": question_label}
    return {
        "breadcrumb": [text_crumb, str(_("userInsightsAllResponses"))],
        "starred_count": 0,
        "total_count": len(table_rows),
        "all_responses": {
            "breadcrumb": [indicator_name, text_crumb, str(_("userInsightsAllResponses"))],
            "total_count": len(table_rows),
            "rows": table_rows,
        },
        "responses": preview,
    }


def _lead_question_from_rows(
    number,
    question_id,
    question_text,
    rows,
    channel,
    indicator_name,
    na_label,
    *,
    expanded=False,
):
    open_text = rows and all(_is_open_text_row(row) for row in rows)
    question_code = f"Q{number:02d}"
    if open_text:
        lead = {
            "id": question_id,
            "number": number,
            "code": question_code,
            "text": question_text,
            "total": len(rows),
            "expanded": expanded,
            "responses": [],
            "response_type": "open_text",
            "active": False,
        }
        lead["text_detail"] = _text_detail_for_rows(
            rows,
            channel,
            question_code,
            indicator_name,
            na_label,
        )
        return lead

    responses, total = _choice_responses_with_followups(rows, channel, number)
    return {
        "id": question_id,
        "number": number,
        "code": question_code,
        "text": question_text,
        "total": total,
        "expanded": expanded,
        "responses": responses,
        "response_type": "choice",
        "active": False,
    }


def _fetch_inline_followups(lead_ids):
    if not lead_ids:
        return []
    ff_qs = FollowupFollowupInlineQuestionResponse.objects.select_related(
        "inline_question", "inline_question_response"
    )
    return list(
        FollowupInlineQuestionResponse.objects.filter(lead_question_id__in=lead_ids)
        .select_related("inline_question", "inline_question_response", "lead_question")
        .prefetch_related(Prefetch("followup_followup_responses", queryset=ff_qs))
        .order_by("id")
    )


def _fetch_messaging_followups(lead_ids):
    if not lead_ids:
        return []
    ff_qs = FollowupFollowupMessagingQuestionResponse.objects.select_related(
        "messaging_question", "messaging_question_response"
    )
    return list(
        FollowupMessagingQuestionResponse.objects.filter(lead_question_id__in=lead_ids)
        .select_related(
            "messaging_question", "messaging_question_response", "lead_question"
        )
        .prefetch_related(Prefetch("followup_followup_responses", queryset=ff_qs))
        .order_by("id")
    )


def _apply_lead_response_filters(qs, *, current_user, filters, channel):
    if not current_user:
        return qs
    filter_fn = (
        lead_inline_question_response_filtered_queryset
        if channel == "inline"
        else lead_messaging_question_response_filtered_queryset
    )
    return filter_fn(current_user, qs, **(filters or {}))


def _fetch_inline_rows(all_keys, *, current_user=None, filters=None):
    if not all_keys:
        return []
    qs = LeadInlineQuestionResponse.objects.filter(
        inline_question__question_key__in=all_keys
    ).select_related("inline_question", "inline_question_response")
    qs = _apply_lead_response_filters(
        qs, current_user=current_user, filters=filters, channel="inline"
    )
    return list(qs.order_by("-question_response_date", "-id"))


def _fetch_messaging_rows(all_keys, *, current_user=None, filters=None):
    if not all_keys:
        return []
    qs = LeadMessagingQuestionResponse.objects.filter(
        messaging_question__question_key__in=all_keys
    ).select_related("messaging_question", "messaging_question_response")
    qs = _apply_lead_response_filters(
        qs, current_user=current_user, filters=filters, channel="messaging"
    )
    return list(qs.order_by("-question_response_date", "-id"))


def _count_responses_in_scope(inline_rows, messaging_rows):
    inline_lead_ids = [row.pk for row in inline_rows]
    messaging_lead_ids = [row.pk for row in messaging_rows]
    inline_followups = _fetch_inline_followups(inline_lead_ids)
    messaging_followups = _fetch_messaging_followups(messaging_lead_ids)
    inline_ff = sum(
        len(list(fu.followup_followup_responses.all())) for fu in inline_followups
    )
    messaging_ff = sum(
        len(list(fu.followup_followup_responses.all())) for fu in messaging_followups
    )
    return (
        len(inline_rows)
        + len(messaging_rows)
        + len(inline_followups)
        + len(messaging_followups)
        + inline_ff
        + messaging_ff
    )


def build_indicator_detail(indicator, *, na_label=None, current_user=None, filters=None):
    """
    Panel payload for one UserInsightsIndicator.

    Lead rows are limited to question keys configured on the indicator (inline + messaging),
    expanded to closely matching catalog variants so follow-up chains stored under legacy keys
    are included, and scoped by the dashboard GenericFilterForm (dates, organisation, etc.).
    Each lead choice includes nested follow-up and follow-up-of-follow-up responses where
    they exist. Configured questions with no matching responses in the current filter
    scope are omitted from the breakdown list.
    """
    if na_label is None:
        na_label = str(_("userInsightsTranslationNA"))

    report_slug = indicator.report.slug
    breakdown_index = indicator.breakdown_index
    panel_dom_id = f"user-insights-panel-{report_slug}-{breakdown_index}"

    inline_links = list(
        indicator.indicator_inline_questions.select_related("question").all()
    )
    messaging_links = list(
        indicator.indicator_messaging_questions.select_related("question").all()
    )

    inline_catalog = list(UniqueInlineQuestion.objects.only("question_key", "question_text"))
    messaging_catalog = list(
        UniqueMessagingQuestion.objects.only("question_key", "question_text")
    )

    inline_keys_by_link = {}
    all_inline_keys = set()
    for link in inline_links:
        if not link.question_id:
            continue
        related = _related_question_keys(
            link.question.question_key,
            link.question.question_text or link.question.question_key,
            inline_catalog,
        )
        inline_keys_by_link[link.pk] = related
        all_inline_keys.update(related)

    messaging_keys_by_link = {}
    all_messaging_keys = set()
    for link in messaging_links:
        if not link.question_id:
            continue
        related = _related_question_keys(
            link.question.question_key,
            link.question.question_text or link.question.question_key,
            messaging_catalog,
        )
        messaging_keys_by_link[link.pk] = related
        all_messaging_keys.update(related)

    inline_rows = (
        _fetch_inline_rows(all_inline_keys, current_user=current_user, filters=filters)
        if all_inline_keys
        else []
    )
    messaging_rows = (
        _fetch_messaging_rows(all_messaging_keys, current_user=current_user, filters=filters)
        if all_messaging_keys
        else []
    )

    inline_by_key = defaultdict(list)
    for row in inline_rows:
        key = row.inline_question.question_key if row.inline_question_id else None
        if key:
            inline_by_key[key].append(row)

    messaging_by_key = defaultdict(list)
    for row in messaging_rows:
        key = row.messaging_question.question_key if row.messaging_question_id else None
        if key:
            messaging_by_key[key].append(row)

    lead_questions = []
    number = 1

    for link in inline_links:
        if not link.question_id:
            continue
        key = link.question.question_key
        text = link.question.question_text or key
        related_keys = inline_keys_by_link.get(link.pk, {key})
        rows = []
        for related_key in related_keys:
            rows.extend(inline_by_key.get(related_key, []))
        if not rows:
            continue
        lead_question = _lead_question_from_rows(
            number,
            _slugify(key, "inline"),
            text,
            rows,
            "inline",
            indicator.name,
            na_label,
            expanded=False,
        )
        if not _lead_question_has_filtered_responses(lead_question):
            continue
        if lead_question.get("response_type") == "choice":
            lead_question["sunburst"] = _build_sunburst_from_responses(
                lead_question["text"],
                lead_question.get("responses", []),
            )
        lead_questions.append(lead_question)
        number += 1

    for link in messaging_links:
        if not link.question_id:
            continue
        key = link.question.question_key
        text = link.question.question_text or key
        related_keys = messaging_keys_by_link.get(link.pk, {key})
        rows = []
        for related_key in related_keys:
            rows.extend(messaging_by_key.get(related_key, []))
        if not rows:
            continue
        lead_question = _lead_question_from_rows(
            number,
            _slugify(key, "messaging"),
            text,
            rows,
            "messaging",
            indicator.name,
            na_label,
            expanded=False,
        )
        if not _lead_question_has_filtered_responses(lead_question):
            continue
        if lead_question.get("response_type") == "choice":
            lead_question["sunburst"] = _build_sunburst_from_responses(
                lead_question["text"],
                lead_question.get("responses", []),
            )
        lead_questions.append(lead_question)
        number += 1

    expanded_question = _pick_expanded_lead_question(lead_questions)
    choice_breadcrumb = []
    sunburst = []
    sunburst_highlight = ""
    if expanded_question:
        expanded_question["expanded"] = True
        if expanded_question.get("response_type") == "choice":
            answer_crumbs = _apply_default_drilldown_selection(
                expanded_question.get("responses", [])
            )
            if answer_crumbs:
                choice_breadcrumb = [expanded_question.get("code") or f"Q{expanded_question['number']:02d}"] + answer_crumbs
            sunburst = _build_sunburst_from_responses(
                expanded_question["text"],
                expanded_question.get("responses", []),
            )
            sunburst_highlight = choice_breadcrumb[-1] if choice_breadcrumb else ""

    all_dates = [
        _response_date(row)
        for row in inline_rows + messaging_rows
        if _response_date(row)
    ]
    date_from = min(all_dates) if all_dates else None
    date_to = max(all_dates) if all_dates else None
    user_responses = _count_responses_in_scope(inline_rows, messaging_rows)

    return {
        "indicator_name": indicator.name,
        "user_responses": user_responses,
        "date_from": date_from.isoformat() if isinstance(date_from, datetime) else (
            date_from.isoformat() if isinstance(date_from, date) else ""
        ),
        "date_to": date_to.isoformat() if isinstance(date_to, datetime) else (
            date_to.isoformat() if isinstance(date_to, date) else ""
        ),
        "date_from_display": _format_date(date_from),
        "date_to_display": _format_date(date_to),
        "panel_script_id": f"user-insights-drilldown-{report_slug}-{breakdown_index}",
        "panel_dom_id": panel_dom_id,
        "lead_questions": lead_questions,
        "choice_breadcrumb": choice_breadcrumb,
        "breadcrumb": choice_breadcrumb,
        "sunburst": sunburst,
        "sunburst_highlight": sunburst_highlight,
    }
