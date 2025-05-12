"""API routes for the chat system."""

from django.urls import path
from . import views

urlpatterns = [
    path('query/', views.chat_endpoint, name='chat_endpoint'),
    path('clear/', views.clear_chat, name='clear_chat'),
]
