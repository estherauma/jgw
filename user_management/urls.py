from django.urls import path
from .views import CreateOrganisationView, user_management


app_name = "user_management"

urlpatterns = [
    path('', user_management, name="home"),
    path('organisations/create/', CreateOrganisationView.as_view(), name="create_organisation"),
    path('organisations/<int:org_id>/edit/', CreateOrganisationView.as_view(), name="edit_organisation"),
]
