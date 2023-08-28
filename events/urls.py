from django.urls import path
from .views import (
    what_matters_to_workers,
)


app_name = "events"

urlpatterns = [
    path("what-matters/", what_matters_to_workers, name="what_matters_to_workers"),
]