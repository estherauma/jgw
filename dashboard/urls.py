from django.urls import path
from . import views

urlpatterns = [
    # Views
    path('', views.index ),
    path('inline-questions', views.inline),
    path('inline-questions/export', views.export_inline),
    path('preferences/export', views.export_preferences),
    # Data for Display
    path('test-preferences', views.retrieve_preferences),
    path('trigger-sentry', views.test_sentry)
]



