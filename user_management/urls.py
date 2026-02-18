from django.urls import path
from .views import CreateOrganisationView, user_management, EditOrganisationView,CreateWorkCodeView,CreateWorkGroupView


app_name = "user_management"

urlpatterns = [
    path('', user_management, name="home"),
    path('organisations/create/', CreateOrganisationView.as_view(), name="create_organisation"),
    path('organisations/<int:organisation_id>/edit/', EditOrganisationView.as_view(), name="edit_organisation"),
    path('work-codes/create/', CreateWorkCodeView.as_view(), name="create_work_code"),
    path('work-groups/create/', CreateWorkGroupView.as_view(), name="create_work_group"),
]
