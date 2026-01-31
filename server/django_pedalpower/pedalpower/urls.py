"""
URL configuration for Pedal Power API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TelemetryViewSet, DashboardView

app_name = 'pedalpower'

router = DefaultRouter()
router.register(r'telemetry', TelemetryViewSet, basename='telemetry')

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('api/', include(router.urls)),
]
