"""jgwpandas URL Configuration
"""

from django.urls import path
from .views import (help_contact_clicks)


app_name = "help_contact_clicks"

urlpatterns = [
    path("help-contact-clicks/", help_contact_clicks, name="help_contact_clicks"),
]