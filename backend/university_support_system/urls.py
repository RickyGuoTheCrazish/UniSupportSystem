"""
Main URL routing for the application.
"""
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Removed admin URLs as admin app is not needed for this demo
    path('api/', include('chat_system.api_routes')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
