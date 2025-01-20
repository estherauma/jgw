from django.urls import path
from .views import (
    export_link_clicks_data,
    export_telephone_clicks_data,
    what_matters_to_workers,
    export_what_matters_to_workers_stats,
    export_report_issue_data,
)


app_name = "events"

urlpatterns = [
    path("what-matters/", what_matters_to_workers, name="what_matters_to_workers"),
    path(
        "what-matters/export-what-matters-stats/",
        export_what_matters_to_workers_stats,
        name="export_what_matters_to_workers_stats",
    ),
    path("what-matters/export-link-clicks/", export_link_clicks_data, name="export_link_clicks_data"),
    path(
        "what-matters/export-telephone-clicks/",
        export_telephone_clicks_data,
        name="export_telephone_clicks_data",
    ),
    path("export-report-issue-data/", export_report_issue_data, name="export_report_issue_data"),
]
