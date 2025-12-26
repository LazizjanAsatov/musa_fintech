from django.contrib import admin
from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'type', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['owner', 'type', 'amount', 'category', 'date', 'created_at']
    list_filter = ['type', 'date', 'created_at']
    search_fields = ['note', 'owner__username']
    date_hierarchy = 'date'

