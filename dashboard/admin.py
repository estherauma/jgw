from django.contrib import admin

from .models import (Factory, JGWCache, Scheme, TranslatedQuestionText,
                     TranslatedResponseText, TranslatedText, Route)


class GenericTranslatedTextAdminDisplay(admin.ModelAdmin):
    """This adds search and table view for the tranlation tables"""
    list_display = ['id','original_text', 'translation']
    search_fields = ['original_text', 'translation']
    
admin.site.register(TranslatedQuestionText, GenericTranslatedTextAdminDisplay)
admin.site.register(TranslatedResponseText, GenericTranslatedTextAdminDisplay)
admin.site.register(TranslatedText, GenericTranslatedTextAdminDisplay)
admin.site.register(JGWCache)
admin.site.register(Scheme)
admin.site.register(Factory)
admin.site.register(Route)
