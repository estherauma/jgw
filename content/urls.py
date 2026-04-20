from django.urls import path
from content.views import (
    StartContentAggregation, AggregatedContentView, ContentWebhookView
)
app_name = 'content'

urlpatterns = [
    path('start-aggregation/', StartContentAggregation.as_view(), name='start'),
    path('aggregated-content/', AggregatedContentView.as_view(), name='get-aggregated-content'),
    path('webhooks/', ContentWebhookView.as_view(), name='content_webhook'),
]
