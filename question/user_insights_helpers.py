"""
Helpers for resolving User Insights configuration from lead question keys.

Relationship chain (inline):
  question_key → UniqueInlineQuestion.question_key
  → UserInsightsIndicatorInlineQuestion.question
  → UserInsightsIndicator (via .indicator)
  → LeadInlineQuestionResponse.question_indicators (M2M)
"""

from question.user_insights_models import (
    UserInsightsIndicator,
    UserInsightsIndicatorInlineQuestion,
    UserInsightsIndicatorMessagingQuestion,
)


def _normalize_question_key(question_key):
    return (question_key or "").strip()


def get_indicator_inline_questions_for_question_key(question_key):
    """
    Return UserInsightsIndicatorInlineQuestion rows configured for this question key.

    Matches admin links where UniqueInlineQuestion.question_key equals question_key.
    """
    key = _normalize_question_key(question_key)
    if not key:
        return UserInsightsIndicatorInlineQuestion.objects.none()
    return (
        UserInsightsIndicatorInlineQuestion.objects.filter(question__question_key=key)
        .select_related("indicator", "indicator__report", "question")
        .order_by("indicator__report__display_order", "indicator__name")
    )


def get_user_insights_indicators_for_inline_question_key(question_key):
    """
    Return UserInsightsIndicator instances to assign on LeadInlineQuestionResponse.question_indicators.
    """
    key = _normalize_question_key(question_key)
    if not key:
        return UserInsightsIndicator.objects.none()
    return (
        UserInsightsIndicator.objects.filter(
            indicator_inline_questions__question__question_key=key,
        )
        .select_related("report")
        .distinct()
        .order_by("report__display_order", "display_order", "name")
    )


def get_indicator_messaging_questions_for_question_key(question_key):
    """Return UserInsightsIndicatorMessagingQuestion rows for a messaging question key."""
    key = _normalize_question_key(question_key)
    if not key:
        return UserInsightsIndicatorMessagingQuestion.objects.none()
    return (
        UserInsightsIndicatorMessagingQuestion.objects.filter(question__question_key=key)
        .select_related("indicator", "indicator__report", "question")
        .order_by("indicator__report__display_order", "indicator__name")
    )


def get_user_insights_indicators_for_messaging_question_key(question_key):
    """Return UserInsightsIndicator instances for LeadMessagingQuestionResponse.question_indicators."""
    key = _normalize_question_key(question_key)
    if not key:
        return UserInsightsIndicator.objects.none()
    return (
        UserInsightsIndicator.objects.filter(
            indicator_messaging_questions__question__question_key=key,
        )
        .select_related("report")
        .distinct()
        .order_by("report__display_order", "display_order", "name")
    )


def rebuild_lead_inline_question_indicators(*, batch_size=2000):
    """
    Clear question_indicators on every LeadInlineQuestionResponse, then reassign
    from UserInsightsIndicatorInlineQuestion using each row's inline question_key.
    """
    from collections import defaultdict

    from question.models import LeadInlineQuestionResponse

    through = LeadInlineQuestionResponse.question_indicators.through
    lead_field = through._meta.get_field("leadinlinequestionresponse")
    indicator_field = through._meta.get_field("userinsightsindicator")

    cleared = through.objects.count()
    through.objects.all().delete()

    key_to_indicator_ids = defaultdict(set)
    for link in UserInsightsIndicatorInlineQuestion.objects.select_related("question"):
        key = _normalize_question_key(
            link.question.question_key if link.question_id else ""
        )
        if key:
            key_to_indicator_ids[key].add(link.indicator_id)

    leads = (
        LeadInlineQuestionResponse.objects.filter(inline_question__isnull=False)
        .exclude(inline_question__question_key__isnull=True)
        .exclude(inline_question__question_key="")
        .values_list("pk", "inline_question__question_key")
    )

    relations = []
    linked_leads = 0
    skipped_leads = 0
    for lead_id, question_key in leads.iterator():
        indicator_ids = key_to_indicator_ids.get(_normalize_question_key(question_key))
        if not indicator_ids:
            skipped_leads += 1
            continue
        linked_leads += 1
        for indicator_id in indicator_ids:
            relations.append(
                through(
                    **{
                        lead_field.attname: lead_id,
                        indicator_field.attname: indicator_id,
                    }
                )
            )

    if relations:
        through.objects.bulk_create(relations, batch_size=batch_size, ignore_conflicts=True)

    return {
        "cleared": cleared,
        "linked_leads": linked_leads,
        "skipped_leads": skipped_leads,
        "relations_created": len(relations),
        "configured_keys": len(key_to_indicator_ids),
    }


def rebuild_lead_messaging_question_indicators(*, batch_size=2000):
    """
    Clear question_indicators on every LeadMessagingQuestionResponse, then reassign
    from UserInsightsIndicatorMessagingQuestion using each row's messaging question_key.
    """
    from collections import defaultdict

    from question.models import LeadMessagingQuestionResponse

    through = LeadMessagingQuestionResponse.question_indicators.through
    lead_field = through._meta.get_field("leadmessagingquestionresponse")
    indicator_field = through._meta.get_field("userinsightsindicator")

    cleared = through.objects.count()
    through.objects.all().delete()

    key_to_indicator_ids = defaultdict(set)
    for link in UserInsightsIndicatorMessagingQuestion.objects.select_related("question"):
        key = _normalize_question_key(
            link.question.question_key if link.question_id else ""
        )
        if key:
            key_to_indicator_ids[key].add(link.indicator_id)

    leads = (
        LeadMessagingQuestionResponse.objects.filter(messaging_question__isnull=False)
        .exclude(messaging_question__question_key__isnull=True)
        .exclude(messaging_question__question_key="")
        .values_list("pk", "messaging_question__question_key")
    )

    relations = []
    linked_leads = 0
    skipped_leads = 0
    for lead_id, question_key in leads.iterator():
        indicator_ids = key_to_indicator_ids.get(_normalize_question_key(question_key))
        if not indicator_ids:
            skipped_leads += 1
            continue
        linked_leads += 1
        for indicator_id in indicator_ids:
            relations.append(
                through(
                    **{
                        lead_field.attname: lead_id,
                        indicator_field.attname: indicator_id,
                    }
                )
            )

    if relations:
        through.objects.bulk_create(relations, batch_size=batch_size, ignore_conflicts=True)

    return {
        "cleared": cleared,
        "linked_leads": linked_leads,
        "skipped_leads": skipped_leads,
        "relations_created": len(relations),
        "configured_keys": len(key_to_indicator_ids),
    }
