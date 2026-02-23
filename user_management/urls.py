from django.urls import path
from .views import (
    CreateAppUserView,
    CreateOrganisationView,
    CreateWorkCodeView,
    CreateWorkGroupView,
    user_management,
    EditAppUserView,
)


app_name = "user_management"

urlpatterns = [
    path('', user_management, name="home"),
    path('organisations/create/', CreateOrganisationView.as_view(), name="create_organisation"),
    path('work-codes/create/', CreateWorkCodeView.as_view(), name="create_work_code"),
    path('work-groups/create/', CreateWorkGroupView.as_view(), name="create_work_group"),
    path('app-users/create/', CreateAppUserView.as_view(), name="create_app_user"),
    path('app-users/<int:user_id>/edit/', EditAppUserView.as_view(), name="edit_app_user"),
]
