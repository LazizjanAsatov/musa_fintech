from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('transactions/', views.transaction_list_view, name='transaction_list'),
    path('transactions/new/', views.transaction_create_view, name='transaction_create'),
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/new/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit_view, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),
]

