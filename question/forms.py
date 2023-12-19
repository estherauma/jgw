from django import forms

from core.forms import GenericFilterForm
from question.models import InlineQuestionText, MessagingQuestionText


def current_inline_questions():
    return [
        (inline_question.text, inline_question.title_text or inline_question.text)
        for inline_question in InlineQuestionText.objects.all()
    ]


class InlineQuestionFilterForm(GenericFilterForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MessagingQuestionFilterForm(GenericFilterForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InlineQuestionOnlyFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["inline_questions"].choices = current_inline_questions()

    inline_questions = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select selectpicker",
                "data-live-search": "true",
                "id": "all-inline-question-select-id",
                "onchange": "handleInlineQuestionsChange()",
            }
        ),
        required=False,
    )
