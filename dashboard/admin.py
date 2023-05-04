from django.contrib import admin

from .models import (Factory, JGWCache, Scheme, TranslatedQuestionText,
                     TranslatedResponseText, TranslatedText, Route)


class TranslatedTextDisplay(admin.ModelAdmin):
    """This adds search and table view for the TranslatedTexts"""
    list_display = ['id','original_text', 'translation']
    search_fields = ['original_text']
    
admin.site.register(TranslatedQuestionText)
admin.site.register(TranslatedResponseText)
admin.site.register(TranslatedText, TranslatedTextDisplay)
admin.site.register(JGWCache)
admin.site.register(Scheme)
admin.site.register(Factory)
admin.site.register(Route)
