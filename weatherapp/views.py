"""
Weather Views - Handle HTTP requests and render templates
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .services import WeatherService
from .models import WeatherQuery, FavoriteCity
import logging
import time

logger = logging.getLogger(__name__)


def index(request):
    """
    Render the main weather app page
    """
    # Get recent queries for display (optional)
    recent_queries = WeatherQuery.objects.all()[:10]
    
    # Get popular cities (optional)
    popular_cities = FavoriteCity.objects.order_by('-query_count')[:5]
    
    context = {
        'recent_queries': recent_queries,
        'popular_cities': popular_cities,
    }
    
    return render(request, 'weather/index.html', context)


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
    
    # Fetch weather data using the service
    weather_service = WeatherService()
    weather_data = weather_service.get_weather(city)
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    weather_data['response_time_ms'] = response_time_ms
    
    # Log the query to database (optional)
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
            logger.error(f"Error logging weather query: {str(e)}")
    
    # Return response
    if weather_data.get('success'):
        logger.info(f"✅ Weather request successful: {city} ({response_time_ms}ms, cache: {weather_data.get('from_cache')})")
        return JsonResponse(weather_data)
    else:
        logger.warning(f"❌ Weather request failed: {city} - {weather_data.get('error')}")
        return JsonResponse(weather_data, status=400)


@require_http_methods(["GET"])
def get_forecast(request):
    """
    API endpoint to get weather forecast for a city
    
    Query params:
        city: City name (required)
        days: Number of days (optional, default 5)
    
    Returns:
        JSON response with forecast data or error
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
    
    # Fetch forecast data
    weather_service = WeatherService()
    forecast_data = weather_service.get_forecast(city, days)
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    forecast_data['response_time_ms'] = response_time_ms
    
    # Return response
    if forecast_data.get('success'):
        logger.info(f"✅ Forecast request successful: {city} ({response_time_ms}ms)")
        return JsonResponse(forecast_data)
    else:
        logger.warning(f"❌ Forecast request failed: {city}")
        return JsonResponse(forecast_data, status=400)


@require_http_methods(["GET"])
def weather_stats(request):
    """
    API endpoint to get weather query statistics
    
    Returns:
        JSON response with statistics
    """
    from django.db.models import Count, Avg, Q
    
    # Total queries
    total_queries = WeatherQuery.objects.count()
    
    # Cache hit rate
    cache_hits = WeatherQuery.objects.filter(from_cache=True).count()
    cache_hit_rate = (cache_hits / total_queries * 100) if total_queries > 0 else 0
    
    # Average response time
    avg_response_time = WeatherQuery.objects.aggregate(
        Avg('response_time_ms')
    )['response_time_ms__avg'] or 0
    
    # Average response time by cache status
    avg_cached_time = WeatherQuery.objects.filter(from_cache=True).aggregate(
        Avg('response_time_ms')
    )['response_time_ms__avg'] or 0
    
    avg_api_time = WeatherQuery.objects.filter(from_cache=False).aggregate(
        Avg('response_time_ms')
    )['response_time_ms__avg'] or 0
    
    # Most queried cities
    top_cities = WeatherQuery.objects.values('city', 'country').annotate(
        query_count=Count('id')
    ).order_by('-query_count')[:10]
    
    # Recent queries
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
@csrf_exempt  # For testing - remove in production and use proper CSRF tokens
def clear_cache(request):
    """
    API endpoint to clear weather cache
    
    POST data:
        city: City name (optional). If not provided, clears all cache
    
    Returns:
        JSON response with success status
    """
    city = request.POST.get('city', '').strip()
    
    weather_service = WeatherService()
    
    try:
        weather_service.clear_cache(city if city else None)
        
        message = f"Cache cleared for {city}" if city else "All weather cache cleared"
        logger.info(message)
        
        return JsonResponse({
            'success': True,
            'message': message
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to clear cache',
            'details': str(e)
        }, status=500)


def about(request):
    """
    Render about page with architecture information
    """
    return render(request, 'weather/about.html')


def stats_page(request):
    """
    Render statistics page
    """
    from django.db.models import Count, Avg
    
    # Get statistics
    total_queries = WeatherQuery.objects.count()
    cache_hits = WeatherQuery.objects.filter(from_cache=True).count()
    cache_hit_rate = (cache_hits / total_queries * 100) if total_queries > 0 else 0
    
    # Top cities
    top_cities = WeatherQuery.objects.values('city', 'country').annotate(
        query_count=Count('id'),
        avg_temp=Avg('temperature')
    ).order_by('-query_count')[:10]
    
    # Recent queries
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