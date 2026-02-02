"""
Weather app URL configuration
"""
from django.urls import path
from . import views

app_name = 'weatherapp'

urlpatterns = [
    # Main page
    path('', views.index, name='index'),
    
    # API endpoints
    path('api/weather/', views.get_weather, name='get_weather'),
    path('api/forecast/', views.get_forecast, name='get_forecast'),
    path('api/stats/', views.weather_stats, name='weather_stats'),
    path('api/clear-cache/', views.clear_cache, name='clear_cache'),
    
    # Additional pages
    path('about/', views.about, name='about'),
    path('stats/', views.stats_page, name='stats_page'),
]