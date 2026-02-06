"""
Complete Weather App Views
All view functions in one place
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg
from django.utils import timezone

from .services import WeatherService
from .enhanced_geolocation_service import EnhancedGeolocationService
from .models import WeatherQuery, FavoriteCity

import logging
import time

logger = logging.getLogger(__name__)


# ===================================================================
# PAGE VIEWS
# ===================================================================

def index(request):
    """Render the main weather app page"""
    recent_queries = WeatherQuery.objects.all()[:10]
    popular_cities = FavoriteCity.objects.order_by('-query_count')[:6]
    
    context = {
        'recent_queries': recent_queries,
        'popular_cities': popular_cities,
    }
    
    return render(request, 'weather/index.html', context)


def about(request):
    """Render about page"""
    return render(request, 'weather/about.html')


def stats_page(request):
    """Render statistics page"""
    total_queries = WeatherQuery.objects.count()
    cache_hits = WeatherQuery.objects.filter(from_cache=True).count()
    cache_hit_rate = (cache_hits / total_queries * 100) if total_queries > 0 else 0
    
    top_cities = WeatherQuery.objects.values('city', 'country').annotate(
        query_count=Count('id'),
        avg_temp=Avg('temperature')
    ).order_by('-query_count')[:10]
    
    recent_queries = WeatherQuery.objects.all()[:20]
    
    context = {
        'total_queries': total_queries,
        'cache_hits': cache_hits,
        'cache_misses': total_queries - cache_hits,
        'cache_hit_rate': round(cache_hit_rate, 2),
        'top_cities': top_cities,
        'recent_queries': recent_queries,
    }
    
    return render(request, 'weather/stats.html', context)


# ===================================================================
# WEATHER API ENDPOINTS
# ===================================================================

@require_http_methods(["GET"])
def get_weather(request):
    """
    API endpoint to get current weather data for a city
    
    Query params:
        city: City name (required)
    
    Returns:
        JSON response with weather data or error
    """
    start_time = time.time()
    
    city = request.GET.get('city', '').strip()
    
    if not city:
        return JsonResponse({
            'success': False,
            'error': 'City parameter is required'
        }, status=400)
    
    # Fetch weather data
    weather_service = WeatherService()
    weather_data = weather_service.get_weather(city)
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    weather_data['response_time_ms'] = response_time_ms
    
    # Log query to database
    if weather_data.get('success'):
        try:
            WeatherQuery.objects.create(
                city=weather_data.get('city', city),
                country=weather_data.get('country', ''),
                temperature=weather_data.get('temperature'),
                description=weather_data.get('description', ''),
                from_cache=weather_data.get('from_cache', False),
                response_time_ms=response_time_ms
            )
            
            # Update favorite city stats
            favorite, created = FavoriteCity.objects.get_or_create(
                city=weather_data.get('city', city),
                defaults={'country': weather_data.get('country', '')}
            )
            favorite.increment_query_count()
            
        except Exception as e:
            logger.error(f"Error logging query: {str(e)}")
    
    if weather_data.get('success'):
        logger.info(f"✅ Weather: {city} ({response_time_ms}ms, cache: {weather_data.get('from_cache')})")
        return JsonResponse(weather_data)
    else:
        logger.warning(f"❌ Weather failed: {city}")
        return JsonResponse(weather_data, status=400)


@require_http_methods(["GET"])
def get_forecast(request):
    """
    API endpoint to get weather forecast
    
    Query params:
        city: City name (required)
        days: Number of days (optional, default 5)
    
    Returns:
        JSON response with forecast data
    """
    start_time = time.time()
    
    city = request.GET.get('city', '').strip()
    
    try:
        days = int(request.GET.get('days', 5))
        if days < 1 or days > 5:
            days = 5
    except ValueError:
        days = 5
    
    if not city:
        return JsonResponse({
            'success': False,
            'error': 'City parameter is required'
        }, status=400)
    
    weather_service = WeatherService()
    forecast_data = weather_service.get_forecast(city, days)
    
    response_time_ms = int((time.time() - start_time) * 1000)
    forecast_data['response_time_ms'] = response_time_ms
    
    if forecast_data.get('success'):
        logger.info(f"✅ Forecast: {city} ({response_time_ms}ms)")
        return JsonResponse(forecast_data)
    else:
        logger.warning(f"❌ Forecast failed: {city}")
        return JsonResponse(forecast_data, status=400)


@require_http_methods(["GET"])
def weather_stats(request):
    """
    API endpoint to get statistics
    
    Returns:
        JSON response with statistics
    """
    total_queries = WeatherQuery.objects.count()
    cache_hits = WeatherQuery.objects.filter(from_cache=True).count()
    cache_hit_rate = (cache_hits / total_queries * 100) if total_queries > 0 else 0
    
    avg_response_time = WeatherQuery.objects.aggregate(
        Avg('response_time_ms')
    )['response_time_ms__avg'] or 0
    
    avg_cached_time = WeatherQuery.objects.filter(from_cache=True).aggregate(
        Avg('response_time_ms')
    )['response_time_ms__avg'] or 0
    
    avg_api_time = WeatherQuery.objects.filter(from_cache=False).aggregate(
        Avg('response_time_ms')
    )['response_time_ms__avg'] or 0
    
    top_cities = WeatherQuery.objects.values('city', 'country').annotate(
        query_count=Count('id')
    ).order_by('-query_count')[:10]
    
    recent_queries = WeatherQuery.objects.values(
        'city', 'country', 'temperature', 'description', 
        'query_time', 'from_cache', 'response_time_ms'
    )[:20]
    
    stats = {
        'success': True,
        'total_queries': total_queries,
        'cache_hits': cache_hits,
        'cache_misses': total_queries - cache_hits,
        'cache_hit_rate': round(cache_hit_rate, 2),
        'avg_response_time_ms': round(avg_response_time, 2),
        'avg_cached_response_time_ms': round(avg_cached_time, 2),
        'avg_api_response_time_ms': round(avg_api_time, 2),
        'top_cities': list(top_cities),
        'recent_queries': list(recent_queries),
    }
    
    return JsonResponse(stats)


@require_http_methods(["POST"])
@csrf_exempt
def clear_cache(request):
    """
    API endpoint to clear cache
    
    POST data:
        city: City name (optional)
    
    Returns:
        JSON response
    """
    city = request.POST.get('city', '').strip()
    
    weather_service = WeatherService()
    
    try:
        weather_service.clear_cache(city if city else None)
        message = f"Cache cleared for {city}" if city else "All cache cleared"
        logger.info(message)
        
        return JsonResponse({
            'success': True,
            'message': message
        })
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to clear cache',
            'details': str(e)
        }, status=500)


# ===================================================================
# GEOLOCATION API ENDPOINTS (ENHANCED)
# ===================================================================

@require_http_methods(["GET"])
def get_weather_by_coordinates_enhanced(request):
    """
    ENHANCED: Get weather by GPS coordinates with better accuracy
    
    Query params:
        lat: Latitude (required)
        lon: Longitude (required)
        show_nearby: If true, also return nearby cities (optional)
    
    Returns:
        JSON response with location and weather data
    """
    try:
        latitude = float(request.GET.get('lat', 0))
        longitude = float(request.GET.get('lon', 0))
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'error': 'Invalid coordinates',
            'details': 'Latitude and longitude must be valid numbers'
        }, status=400)
    
    if not latitude or not longitude:
        return JsonResponse({
            'success': False,
            'error': 'Missing coordinates',
            'details': 'Both latitude and longitude are required'
        }, status=400)
    
    # Use enhanced geolocation service
    geo_service = EnhancedGeolocationService()
    location_data = geo_service.get_precise_location(latitude, longitude)
    
    if not location_data.get('success'):
        return JsonResponse(location_data, status=400)
    
    # Get the city name
    city = location_data.get('city')
    
    # Log detection
    logger.info(f"📍 Detected: {city}")
    logger.info(f"   Source: {location_data.get('source')}")
    logger.info(f"   Accuracy: {location_data.get('accuracy')}")
    if location_data.get('suburb'):
        logger.info(f"   Suburb: {location_data.get('suburb')}")
    
    # Get weather
    weather_service = WeatherService()
    weather_data = weather_service.get_weather(city)
    
    if weather_data.get('success'):
        response = {
            **weather_data,
            'location_detected': True,
            'detected_from': 'gps',
            'detection_accuracy': location_data.get('accuracy', 'medium'),
            'detection_source': location_data.get('source', 'unknown'),
            'suburb': location_data.get('suburb', ''),
            'state': location_data.get('state', ''),
            'display_name': location_data.get('display_name', ''),
            'coordinates': {
                'lat': latitude,
                'lon': longitude
            }
        }
        
        # Include nearby cities if requested
        show_nearby = request.GET.get('show_nearby', 'false').lower() == 'true'
        if show_nearby:
            nearby = geo_service.get_nearby_cities(latitude, longitude, radius=30)
            if nearby.get('success'):
                response['nearby_cities'] = nearby.get('cities', [])[:5]
        
        logger.info(f"✅ Weather for precise location: {city}")
        return JsonResponse(response)
    else:
        # Offer nearby alternatives
        logger.warning(f"⚠️ No weather for {city}, finding alternatives...")
        
        nearby = geo_service.get_nearby_cities(latitude, longitude, radius=50)
        if nearby.get('success') and nearby.get('cities'):
            return JsonResponse({
                'success': False,
                'error': f'No weather data for {city}',
                'details': 'Try one of the nearby cities',
                'location_detected': location_data,
                'nearby_cities': nearby.get('cities', [])[:10],
                'suggestion': f"Try: {nearby['cities'][0]['city']}"
            }, status=404)
        else:
            return JsonResponse(weather_data, status=400)


@require_http_methods(["GET"])
def get_nearby_cities(request):
    """
    Get cities near coordinates
    
    Query params:
        lat: Latitude (required)
        lon: Longitude (required)
        radius: Search radius in km (optional, default 50)
    
    Returns:
        JSON response with nearby cities
    """
    try:
        latitude = float(request.GET.get('lat', 0))
        longitude = float(request.GET.get('lon', 0))
        radius = int(request.GET.get('radius', 50))
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'error': 'Invalid parameters'
        }, status=400)
    
    if not latitude or not longitude:
        return JsonResponse({
            'success': False,
            'error': 'Missing coordinates'
        }, status=400)
    
    geo_service = EnhancedGeolocationService()
    result = geo_service.get_nearby_cities(latitude, longitude, radius)
    
    return JsonResponse(result)


@require_http_methods(["GET"])
def reverse_geocode_enhanced(request):
    """
    ENHANCED: Reverse geocoding with better accuracy
    
    Query params:
        lat: Latitude (required)
        lon: Longitude (required)
    
    Returns:
        JSON response with location info
    """
    try:
        latitude = float(request.GET.get('lat', 0))
        longitude = float(request.GET.get('lon', 0))
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'error': 'Invalid coordinates'
        }, status=400)
    
    if not latitude or not longitude:
        return JsonResponse({
            'success': False,
            'error': 'Missing coordinates'
        }, status=400)
    
    geo_service = EnhancedGeolocationService()
    location_data = geo_service.get_precise_location(latitude, longitude)
    
    if location_data.get('success'):
        return JsonResponse(location_data)
    else:
        return JsonResponse(location_data, status=400)


@require_http_methods(["GET"])
def search_cities(request):
    """
    Search cities by name (for autocomplete)
    
    Query params:
        q: Search query (required)
        limit: Max results (optional, default 5)
    
    Returns:
        JSON response with matching cities
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({
            'success': False,
            'error': 'Search query is required'
        }, status=400)
    
    try:
        limit = int(request.GET.get('limit', 5))
        limit = min(limit, 10)
    except ValueError:
        limit = 5
    
    # Use the geolocation service for city search
    from .geolocation_service import GeolocationService
    geo_service = GeolocationService()
    results = geo_service.search_cities(query, limit)
    
    return JsonResponse(results)