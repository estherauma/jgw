"""
Configuration models for the User Insights reporting UI.

Links reports → indicators → unique lead questions (inline or messaging).
Analytics query LeadInlineQuestionResponse / LeadMessagingQuestionResponse
by matching question_key on the linked Unique*Question row.
"""

from django.db import models


class UserInsightsReport(models.Model):
    """Top-level report (e.g. early risk, decent employment)."""

    slug = models.SlugField(max_length=64, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    hint = models.TextField(blank=True)
    pdf_label = models.CharField(max_length=255, blank=True)
    breakdown_header = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "title"]
        verbose_name = "User insights report"
        verbose_name_plural = "User insights reports"

    def __str__(self):
        return self.title


class UserInsightsIndicator(models.Model):
    """
    Risk indicator belonging to a report (donut + breakdown row).

    Linked to lead responses via ManyToMany on LeadInlineQuestionResponse /
    LeadMessagingQuestionResponse (``question_indicators``).
    """

    report = models.ForeignKey(
        UserInsightsReport,
        on_delete=models.CASCADE,
        related_name="indicators",
    )
    slug = models.SlugField(max_length=64)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7, default="#3498db", help_text="Hex color, e.g. #e67e22")
    display_order = models.PositiveSmallIntegerField(default=0)
    breakdown_index = models.PositiveSmallIntegerField(
        default=0,
        help_text="Index used by the breakdown accordion and chart payload.",
    )
    show_on_donut = models.BooleanField(
        default=True,
        help_text="If false, indicator appears in breakdown list only.",
    )
    donut_slot = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Position in the donut row when show_on_donut is true.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["report", "display_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["report", "slug"],
                name="unique_user_insights_indicator_slug_per_report",
            ),
            models.UniqueConstraint(
                fields=["report", "breakdown_index"],
                name="unique_user_insights_indicator_breakdown_index_per_report",
            ),
        ]
        verbose_name = "User insights indicator"
        verbose_name_plural = "User insights indicators"

    def __str__(self):
        return f"{self.report.slug}: {self.name}"


class UserInsightsIndicatorInlineQuestion(models.Model):
    """Lead inline question attached to an indicator."""

    indicator = models.ForeignKey(
        UserInsightsIndicator,
        on_delete=models.CASCADE,
        related_name="indicator_inline_questions",
    )
    question = models.ForeignKey(
        "question.UniqueInlineQuestion",
        on_delete=models.PROTECT,
        related_name="user_insights_indicator_links",
        help_text="Unique inline question (synced from lead responses).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["indicator", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["indicator", "question"],
                name="unique_user_insights_indicator_inline_question",
            ),
        ]
        verbose_name = "User insights indicator inline question"
        verbose_name_plural = "User insights indicator inline questions"

    @property
    def question_key(self):
        return self.question.question_key if self.question_id else ""

    def __str__(self):
        return f"{self.indicator} — inline: {self.question}"


class UserInsightsIndicatorMessagingQuestion(models.Model):
    """Lead messaging question attached to an indicator."""

    indicator = models.ForeignKey(
        UserInsightsIndicator,
        on_delete=models.CASCADE,
        related_name="indicator_messaging_questions",
    )
    question = models.ForeignKey(
        "question.UniqueMessagingQuestion",
        on_delete=models.PROTECT,
        related_name="user_insights_indicator_links",
        help_text="Unique messaging question (synced from lead responses).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["indicator", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["indicator", "question"],
                name="unique_user_insights_indicator_messaging_question",
            ),
        ]
        verbose_name = "User insights indicator messaging question"
        verbose_name_plural = "User insights indicator messaging questions"

    @property
    def question_key(self):
        return self.question.question_key if self.question_id else ""

    def __str__(self):
        return f"{self.indicator} — messaging: {self.question}"
