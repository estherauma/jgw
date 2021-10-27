from django.urls import path
from . import views

urlpatterns = [
    path('', views.index ),
    path('test-preferences', views.retrieve_preferences),
    path('trigger-sentry', views.test_sentry)
]
