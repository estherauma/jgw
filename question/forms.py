from django import forms

from core.forms import GenericFilterForm
from question.models import InlineQuestionText, MessagingQuestionText


def current_inline_questions(inline_question_choices):
    return [
        (choice['title'], choice['title'] or choice['key'])
        for choice in inline_question_choices
    ]


class InlineQuestionFilterForm(GenericFilterForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MessagingQuestionFilterForm(GenericFilterForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InlineQuestionOnlyFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        inline_question_choices = kwargs.pop('inline_question_choices', [])
        super().__init__(*args, **kwargs)

        self.fields["inline_questions"].choices = current_inline_questions(inline_question_choices)

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
