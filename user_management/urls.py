from django.urls import path
from .views import CreateOrganisationView, user_management, EditOrganisationView


app_name = "user_management"

urlpatterns = [
    path('', user_management, name="home"),
    path('organisations/create/', CreateOrganisationView.as_view(), name="create_organisation"),
    path('organisations/<int:organization_id>/edit/', EditOrganisationView.as_view(), name="edit_organisation"),
]
