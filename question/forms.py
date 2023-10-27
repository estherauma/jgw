from django import forms

from core.forms import GenericFilterForm
from question.models import InlineQuestionText, MessagingQuestionText


class InlineQuestionFilterForm(GenericFilterForm):    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["question_texts"].choices = [
            (inline_question.text, inline_question.text) 
            for inline_question in InlineQuestionText.objects.all()
        ]

    question_texts = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={
            "class": "form-select selectpicker", 
            "data-live-search": "true", 
            "id": "inline-question-select-id"
        }),
        required=False
    )
    
class MessagingQuestionFilterForm(GenericFilterForm):    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["question_texts"].choices = [
            (messaging_question.translated_text, messaging_question.translated_text) 
            for messaging_question in MessagingQuestionText.objects.all()
        ]

    question_texts = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={
            "class": "form-select selectpicker", 
            "data-live-search": "true", 
            "id": "messaging-question-select-id"
        }),
        required=False
    )
    

class InlineQuestionOnlyFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["inline_questions"].choices = [
            (inline_question.text, inline_question.text) 
            for inline_question in InlineQuestionText.objects.all()
        ]

    inline_questions = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={
            "class": "form-select selectpicker", 
            "data-live-search": "true", 
            "id": "all-inline-question-select-id",
            "onchange": "handleInlineQuestionsChange()",
        }),
        required=False
    )