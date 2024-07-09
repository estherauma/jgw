from django.urls import path
from .views import (
    export_link_clicks_data,
    what_matters_to_workers,
    export_what_matters_to_workers_stats
)


app_name = "events"

urlpatterns = [
    path("what-matters/", what_matters_to_workers, name="what_matters_to_workers"),
    path("what-matters/export-what-matters-stats/", export_what_matters_to_workers_stats, name="export_what_matters_to_workers_stats"),
    path('what-matters/export-link-clicks/',export_link_clicks_data, name='export_link_clicks_data')
]