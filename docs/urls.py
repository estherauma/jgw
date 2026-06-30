from django.urls import path

from .views import DocsPageView

app_name = "docs"

urlpatterns = [
    path("<slug:section_slug>/<slug:page_slug>/", DocsPageView.as_view(), name="page"),
]
