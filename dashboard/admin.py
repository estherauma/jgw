from django.contrib import admin
from .models import (
    TranslatedQuestionText,
    TranslatedResponseText,
    TranslatedText
)

admin.site.register(TranslatedQuestionText)
admin.site.register(TranslatedResponseText)
admin.site.register(TranslatedText)
