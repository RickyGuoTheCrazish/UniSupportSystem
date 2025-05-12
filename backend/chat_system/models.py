from django.db import models
import uuid
from django.utils import timezone


class UserSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    current_agent = models.CharField(max_length=100, default="triage_agent")
    
    def __str__(self):
        return f"Session {self.session_id} - Last active: {self.last_active}"


class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
        ('tool', 'Tool'),
        ('function', 'Function'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    agent_name = models.CharField(max_length=100, blank=True, null=True)
    function_name = models.CharField(max_length=100, blank=True, null=True)
    function_arguments = models.JSONField(blank=True, null=True)
    function_response = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}{'...' if len(self.content) > 50 else ''}"
