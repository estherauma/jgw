"""Admin forms and helpers for User Insights configuration."""

from django import forms

from question.models import UniqueInlineQuestion, UniqueMessagingQuestion
from question.user_insights_models import (
    UserInsightsIndicator,
    UserInsightsIndicatorInlineQuestion,
    UserInsightsIndicatorMessagingQuestion,
)


def _question_checkbox_field(queryset, *, label, help_text):
    return forms.ModelMultipleChoiceField(
        queryset=queryset,
        required=False,
        label=label,
        help_text=help_text,
        widget=forms.CheckboxSelectMultiple,
    )


class UserInsightsIndicatorAdminForm(forms.ModelForm):
    """Attach many inline / messaging questions via checkboxes on the indicator page."""

    inline_questions = _question_checkbox_field(
        UniqueInlineQuestion.objects.order_by("question_key"),
        label="Inline questions",
        help_text="Select lead inline questions included in this indicator.",
    )
    messaging_questions = _question_checkbox_field(
        UniqueMessagingQuestion.objects.order_by("question_key"),
        label="Messaging questions",
        help_text="Select lead messaging questions included in this indicator.",
    )

    class Meta:
        model = UserInsightsIndicator
        fields = [
            "report",
            "slug",
            "name",
            "color",
            "display_order",
            "breakdown_index",
            "show_on_donut",
            "donut_slot",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["inline_questions"].initial = UniqueInlineQuestion.objects.filter(
                user_insights_indicator_links__indicator=self.instance,
            )
            self.fields["messaging_questions"].initial = UniqueMessagingQuestion.objects.filter(
                user_insights_indicator_links__indicator=self.instance,
            )


def sync_indicator_inline_questions(indicator, selected_questions):
    selected_ids = {question.pk for question in selected_questions}
    indicator.indicator_inline_questions.exclude(question_id__in=selected_ids).delete()
    existing_ids = set(
        indicator.indicator_inline_questions.values_list("question_id", flat=True)
    )
    for question in selected_questions:
        if question.pk not in existing_ids:
            UserInsightsIndicatorInlineQuestion.objects.create(
                indicator=indicator,
                question=question,
            )


def sync_indicator_messaging_questions(indicator, selected_questions):
    selected_ids = {question.pk for question in selected_questions}
    indicator.indicator_messaging_questions.exclude(question_id__in=selected_ids).delete()
    existing_ids = set(
        indicator.indicator_messaging_questions.values_list("question_id", flat=True)
    )
    for question in selected_questions:
        if question.pk not in existing_ids:
            UserInsightsIndicatorMessagingQuestion.objects.create(
                indicator=indicator,
                question=question,
            )


class UserInsightsIndicatorInlineQuestionAdminForm(forms.ModelForm):
    """Configure all inline question links for one indicator via checkboxes."""

    questions = _question_checkbox_field(
        UniqueInlineQuestion.objects.order_by("question_key"),
        label="Inline questions",
        help_text="Select every unique inline question attached to this indicator.",
    )

    class Meta:
        model = UserInsightsIndicatorInlineQuestion
        fields = ("indicator",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.indicator_id:
            self.fields["questions"].initial = UniqueInlineQuestion.objects.filter(
                user_insights_indicator_links__indicator=self.instance.indicator,
            )

    def save(self, commit=True):
        """Links are created in ModelAdmin.save_model; do not save this row here."""
        self.instance.indicator = self.cleaned_data["indicator"]
        if commit:
            self.instance.save()
        else:
            # Required when admin calls form.save(commit=False) then save_m2m().
            self.save_m2m = lambda: None
        return self.instance


class UserInsightsIndicatorMessagingQuestionAdminForm(forms.ModelForm):
    """Configure all messaging question links for one indicator via checkboxes."""

    questions = _question_checkbox_field(
        UniqueMessagingQuestion.objects.order_by("question_key"),
        label="Messaging questions",
        help_text="Select every unique messaging question attached to this indicator.",
    )

    class Meta:
        model = UserInsightsIndicatorMessagingQuestion
        fields = ("indicator",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.indicator_id:
            self.fields["questions"].initial = UniqueMessagingQuestion.objects.filter(
                user_insights_indicator_links__indicator=self.instance.indicator,
            )

    def save(self, commit=True):
        """Links are created in ModelAdmin.save_model; do not save this row here."""
        self.instance.indicator = self.cleaned_data["indicator"]
        if commit:
            self.instance.save()
        else:
            self.save_m2m = lambda: None
        return self.instance
