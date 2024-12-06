"""
URL configuration for core project.
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from comments.router import router as comments_router

api_urls = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('comments/', comments_router.urls),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
]
