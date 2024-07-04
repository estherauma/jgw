from django.urls import path
from . import views

app_name = 'other_resource'

urlpatterns = [
    path('', views.other_resource_view, name='other_resource'),
    path('edit/<int:resource_id>/', views.edit_resource, name='edit_resource'),
    path('delete/<int:resource_id>/', views.delete_resource, name='delete_resource'),
]
