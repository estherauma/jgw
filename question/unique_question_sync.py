"""Sync UniqueInlineQuestion / UniqueMessagingQuestion from lead response data."""

from question.models import (
    LeadInlineQuestionResponse,
    LeadMessagingQuestionResponse,
    UniqueInlineQuestion,
    UniqueMessagingQuestion,
)


def _merge_question_rows(seen, rows):
    for key, text in rows:
        key = (key or "").strip()
        if not key:
            continue
        text = (text or "").strip()
        if key not in seen or (not seen[key] and text):
            seen[key] = text


def sync_unique_inline_questions():
    """Upsert unique inline questions from LeadInlineQuestionResponse only."""
    seen = {}

    _merge_question_rows(
        seen,
        LeadInlineQuestionResponse.objects.filter(inline_question__isnull=False)
        .exclude(inline_question__question_key__isnull=True)
        .exclude(inline_question__question_key="")
        .values_list("inline_question__question_key", "inline_question__question_text"),
    )

    created = updated = 0
    for key, text in seen.items():
        _, was_created = UniqueInlineQuestion.objects.update_or_create(
            question_key=key,
            defaults={"question_text": text},
        )
        if was_created:
            created += 1
        else:
            updated += 1
    return created, updated


def sync_unique_messaging_questions():
    """Upsert unique messaging questions from LeadMessagingQuestionResponse only."""
    seen = {}

    _merge_question_rows(
        seen,
        LeadMessagingQuestionResponse.objects.filter(messaging_question__isnull=False)
        .exclude(messaging_question__question_key__isnull=True)
        .exclude(messaging_question__question_key="")
        .values_list(
            "messaging_question__question_key",
            "messaging_question__question_text",
        ),
    )

    created = updated = 0
    for key, text in seen.items():
        _, was_created = UniqueMessagingQuestion.objects.update_or_create(
            question_key=key,
            defaults={"question_text": text},
        )
        if was_created:
            created += 1
        else:
            updated += 1
    return created, updated
