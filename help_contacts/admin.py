from django.contrib import admin

from help_contacts.models import HelpContact

# Register your models here.
class HelpContactTabularDisplay(admin.ModelAdmin):
    list_display = ['contact_value', 'translated_contact_value', 'contact_type']
    search_fields = ['contact_value', 'translated_contact_value', 'contact_type']
    
admin.site.register(HelpContact, HelpContactTabularDisplay)
