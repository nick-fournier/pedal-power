from django.apps import AppConfig


class PedalPowerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pedalpower'
    verbose_name = 'Pedal Power Monitoring'
    
    def ready(self):
        """Initialize app when Django starts"""
        pass
