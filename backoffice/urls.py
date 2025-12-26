from django.urls import path
from . import views

app_name = 'backoffice'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/<int:pk>/', views.user_detail_view, name='user_detail'),
    path('settings/', views.settings_view, name='settings'),
    path('monitoring/', views.monitoring_view, name='monitoring'),
    path('audit/', views.audit_log_view, name='audit_log'),
]

