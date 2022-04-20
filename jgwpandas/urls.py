"""jgwpandas URL Configuration
"""
from django.contrib import admin
from django.urls import path
from django.urls.conf import include

import dashboard
urlpatterns = [
    # admin site
    path('admin/', admin.site.urls),

    # dashboard
    path('', include('dashboard.urls')),

    # accounts
    path('accounts/', include('users.urls'))
]
