from django.contrib import admin
from .models import UserSession, Message

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'current_agent', 'created_at', 'last_active')
    list_filter = ('current_agent', 'created_at')
    search_fields = ('session_id', 'current_agent')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'agent_name', 'timestamp')
    list_filter = ('role', 'agent_name', 'timestamp')
    search_fields = ('content', 'agent_name', 'function_name')
