"""jgwpandas URL Configuration
"""

from django.urls import path
from . import views 


app_name = "preference"

urlpatterns = [
    path("user-overview/", views.user_overview, name="user_overview"),
    path("user-overview/export-stats", views.export_preference_stats, name="export_preference_stats"),
    path('user-overview/export-returning-users/', views.export_returning_users_to_excel, name='export_returning_users'),
    path('user-overview/export-help-contacts/', views.export_help_contacts_data, name='export_help_contacts'),
    path('user-overview/export-preferences', views.export_preferences_data, name='export_preferences'),
    path('user-overview/export-pay-calculator-statistics', views.export_pay_calculator_statistics, name='export_pay_calculator_statistics'),
    path('user-diagnostics/', views.user_diagnostics, name='user_diagnostics'),
    path('api/dashboard/customize/', views.dashboard_customization, name='dashboard_customize'),
    path('api/monthly-active-users/', views.filter_monthly_active_users, name='filter_monthly_active_users'),
    path('api/users-by-origin/', views.filter_users_by_origin, name='filter_users_by_origin'),
    path('api/users-by-gender/', views.filter_users_by_gender, name='filter_users_by_gender'),
    path('api/users-by-destination/', views.filter_users_by_destination, name='filter_users_by_destination'),
    path('api/users-by-language/', views.filter_users_by_language, name='filter_users_by_language'),
    path('api/users-by-state/', views.filter_users_by_state, name='filter_users_by_state'),
    path('api/users-by-immigration/', views.filter_users_by_immigration, name='filter_users_by_immigration'),
    path('api/users-by-age/', views.filter_users_by_age, name='filter_users_by_age'),
    path('api/users-by-sector/', views.filter_users_by_sector, name='filter_users_by_sector'),
    path('api/work-code-usage/', views.filter_work_code_usage, name='filter_work_code_usage'),
    path('api/new-users-by-month/', views.filter_new_users_by_month, name='filter_new_users_by_month'),
    path('api/dashboard/reset/', views.reset_dashboard, name='dashboard_reset'),
    path('api/chart-settings/', views.chart_settings_api, name='chart_settings_api'),
    path('api/chart-settings/<str:chart_id>/', views.chart_settings_api, name='chart_settings_api_detail'),
]