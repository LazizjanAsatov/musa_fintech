from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'target', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['action', 'target', 'actor__username']
    readonly_fields = ['actor', 'action', 'target', 'metadata', 'created_at']
    date_hierarchy = 'created_at'




