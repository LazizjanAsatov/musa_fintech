"""
URL configuration for fintech_health project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('app/', include('finance.urls')),
    path('backoffice/', include('backoffice.urls')),
]




