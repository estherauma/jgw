from django.urls import path
from . import views
app_name='pipeline'
urlpatterns = [
    path('pipeline-status/', views.pipeline_status, name='pipeline_status'),
]
