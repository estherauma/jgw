from django.contrib import admin

from .models import (Factory, JGWCache, Scheme, TranslatedQuestionText,
                     TranslatedResponseText, TranslatedText)

admin.site.register(TranslatedQuestionText)
admin.site.register(TranslatedResponseText)
admin.site.register(TranslatedText)
admin.site.register(JGWCache)
admin.site.register(Scheme)
admin.site.register(Factory)
