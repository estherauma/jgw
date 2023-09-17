from django.urls import path
from .views import (
    what_matters_to_workers,
    export_what_matters_to_workers_stats
)


app_name = "events"

urlpatterns = [
    path("what-matters/", what_matters_to_workers, name="what_matters_to_workers"),
    path("what-matters/export-what-matters-stats/", export_what_matters_to_workers_stats, name="export_what_matters_to_workers_stats"),
]