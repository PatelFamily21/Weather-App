"""
Weather app configuration
"""
from django.apps import AppConfig


class WeatherappConfig(AppConfig):
    """Configuration for weatherapp"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weatherapp'
    verbose_name = 'Weather Application'
    
    def ready(self):
        """
        Initialize app when Django starts
        This is called once when Django loads the app
        """
        # Import signals here if needed
        # import weatherapp.signals
        pass