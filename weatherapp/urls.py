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

    path('api/weather/coordinates/', views.get_weather_by_coordinates_enhanced, name='weather_by_coordinates'),
    path('api/geocode/reverse/', views.reverse_geocode_enhanced, name='reverse_geocode'),
    path('api/geocode/search/', views.search_cities, name='search_cities'),

    # New Endpoint
    path('api/geocode/nearby/', views.get_nearby_cities, name='get_nearby_cities'),
]