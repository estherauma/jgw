from django.urls import path
from .views import (
    AssignWorkCodeView,
    CreateAppUserView,
    CreateOrganisationView,
    EditOrganisationView,
    CreateWorkCodeView,
    CreateWorkGroupView,
    user_management,
    EditAppUserView,
    search_organisations,
    search_users,
)

app_name = "user_management"

urlpatterns = [
    path('', user_management, name="home"),
    path('organisations/create/', CreateOrganisationView.as_view(), name="create_organisation"),
    path('organisations/search/', search_organisations, name="search_organisations"),
    path('organisations/<int:organisation_id>/edit/', EditOrganisationView.as_view(), name="edit_organisation"),
    path('work-codes/create/', CreateWorkCodeView.as_view(), name="create_work_code"),
    path('work-codes/assign/', AssignWorkCodeView.as_view(), name="assign_work_code"),
    path('work-groups/create/', CreateWorkGroupView.as_view(), name="create_work_group"),
    path('app-users/create/', CreateAppUserView.as_view(), name="create_app_user"),
    path('app-users/search/', search_users, name="search_users"),
    path('app-users/<int:user_id>/edit/', EditAppUserView.as_view(), name="edit_app_user"),
]
