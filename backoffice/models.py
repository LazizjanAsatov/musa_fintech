from django.db import models
from django.contrib.auth.models import User
import json


class AuditLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_actions')
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=200)
    metadata = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} - {self.target} - {self.created_at}"
    
    def set_metadata(self, data):
        """Store metadata as JSON string."""
        self.metadata = json.dumps(data)
    
    def get_metadata(self):
        """Retrieve metadata as dict."""
        if self.metadata:
            try:
                return json.loads(self.metadata)
            except:
                return {}
        return {}


