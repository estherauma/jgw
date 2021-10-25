from django.urls import path
from . import views

urlpatterns = [
    path('', views.index ),
    path('trigger-sentry', views.test_sentry)
]
