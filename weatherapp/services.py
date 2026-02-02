"""
Weather Service - Handles communication with 3rd party Weather API
Implements Redis caching as shown in the architecture diagram
"""
import requests
from django.conf import settings
from django.core.cache import cache
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Service to fetch weather data from 3rd party API with Redis caching
    
    Flow (as per architecture diagram):
    1. Check Redis cache
    2. If cache miss, request from 3rd party Weather API
    3. Cache the response in Redis
    4. Return weather data
    """
    
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_API_BASE_URL
        self.cache_timeout = settings.WEATHER_CACHE_TIMEOUT
    
    def _get_cache_key(self, city: str) -> str:
        """Generate cache key for a city"""
        return f"weather_data_{city.lower().strip()}"
    
    def get_weather(self, city: str) -> dict:
        """
        Get weather data for a city with Redis caching
        
        Args:
            city: City name to get weather for
            
        Returns:
            dict: Weather data or error information
        """
        if not city or not city.strip():
            return {
                'success': False,
                'error': 'City name is required',
                'details': 'Please provide a valid city name'
            }
        
        city = city.strip()
        
        # Step 1: Check Redis cache
        cache_key = self._get_cache_key(city)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.info(f"✅ Cache HIT for city: {city}")
            cached_data['from_cache'] = True
            return cached_data
        
        logger.info(f"❌ Cache MISS for city: {city}")
        
        # Step 2: Request from 3rd party Weather API
        try:
            weather_data = self._fetch_from_api(city)
            
            # Step 3: Save cached results in Redis
            if weather_data.get('success'):
                cache.set(cache_key, weather_data, self.cache_timeout)
                logger.info(f"💾 Cached weather data for city: {city} (TTL: {self.cache_timeout}s)")
            
            weather_data['from_cache'] = False
            return weather_data
            
        except Exception as e:
            logger.error(f"Error fetching weather for {city}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to fetch weather data',
                'details': str(e)
            }
    
    def _fetch_from_api(self, city: str) -> dict:
        """
        Fetch weather data from 3rd party Weather API (OpenWeatherMap)
        
        Args:
            city: City name
            
        Returns:
            dict: Formatted weather data
        """
        url = f"{self.base_url}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'  # Use metric units (Celsius)
        }
        
        try:
            logger.info(f"🌐 Calling OpenWeatherMap API for: {city}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Format the response
            formatted_data = {
                'success': True,
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': round(data['main']['temp'], 1),
                'feels_like': round(data['main']['feels_like'], 1),
                'temp_min': round(data['main'].get('temp_min', 0), 1),
                'temp_max': round(data['main'].get('temp_max', 0), 1),
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_deg': data['wind'].get('deg', 0),
                'clouds': data['clouds']['all'],
                'visibility': data.get('visibility', 0),
                'sunrise': data['sys'].get('sunrise', 0),
                'sunset': data['sys'].get('sunset', 0),
                'timezone': data.get('timezone', 0),
                'timestamp': data['dt'],
                'coord': {
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon']
                }
            }
            
            logger.info(f"✅ Successfully fetched weather for {city}: {formatted_data['temperature']}°C")
            return formatted_data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"City not found: {city}")
                return {
                    'success': False,
                    'error': 'City not found',
                    'details': 'Please check the city name and try again'
                }
            elif e.response.status_code == 401:
                logger.error("Invalid API key")
                return {
                    'success': False,
                    'error': 'Invalid API key',
                    'details': 'Please configure a valid API key in .env file'
                }
            else:
                logger.error(f"HTTP error {e.response.status_code}: {str(e)}")
                return {
                    'success': False,
                    'error': f'API error: {e.response.status_code}',
                    'details': str(e)
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for city: {city}")
            return {
                'success': False,
                'error': 'Request timeout',
                'details': 'The weather service is taking too long to respond'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception for {city}: {str(e)}")
            return {
                'success': False,
                'error': 'Connection error',
                'details': f'Could not connect to weather service: {str(e)}'
            }
    
    def get_forecast(self, city: str, days: int = 5) -> dict:
        """
        Get weather forecast for a city with Redis caching
        
        Args:
            city: City name
            days: Number of days (default 5)
            
        Returns:
            dict: Forecast data or error information
        """
        if not city or not city.strip():
            return {
                'success': False,
                'error': 'City name is required'
            }
        
        city = city.strip()
        
        # Check cache
        cache_key = f"weather_forecast_{city.lower()}_{days}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.info(f"✅ Cache HIT for forecast: {city}")
            cached_data['from_cache'] = True
            return cached_data
        
        logger.info(f"❌ Cache MISS for forecast: {city}")
        
        # Fetch from API
        try:
            forecast_data = self._fetch_forecast_from_api(city, days)
            
            if forecast_data.get('success'):
                cache.set(cache_key, forecast_data, self.cache_timeout)
                logger.info(f"💾 Cached forecast data for city: {city}")
            
            forecast_data['from_cache'] = False
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error fetching forecast for {city}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to fetch forecast data',
                'details': str(e)
            }
    
    def _fetch_forecast_from_api(self, city: str, days: int) -> dict:
        """Fetch forecast data from API"""
        url = f"{self.base_url}/forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'cnt': min(days * 8, 40)  # API returns 3-hour intervals, max 40 (5 days)
        }
        
        try:
            logger.info(f"🌐 Calling OpenWeatherMap Forecast API for: {city}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process forecast data (one forecast per day)
            forecasts = []
            seen_dates = set()
            
            for item in data['list']:
                # Get date from timestamp
                date = datetime.fromtimestamp(item['dt']).date()
                
                # Only include one forecast per day (around noon)
                if date not in seen_dates:
                    forecasts.append({
                        'date': item['dt'],
                        'date_text': item['dt_txt'],
                        'temperature': round(item['main']['temp'], 1),
                        'temp_min': round(item['main']['temp_min'], 1),
                        'temp_max': round(item['main']['temp_max'], 1),
                        'description': item['weather'][0]['description'].title(),
                        'icon': item['weather'][0]['icon'],
                        'humidity': item['main']['humidity'],
                        'wind_speed': item['wind']['speed'],
                        'clouds': item['clouds']['all'],
                    })
                    seen_dates.add(date)
                    
                    if len(forecasts) >= days:
                        break
            
            result = {
                'success': True,
                'city': data['city']['name'],
                'country': data['city']['country'],
                'forecasts': forecasts,
                'forecast_count': len(forecasts)
            }
            
            logger.info(f"✅ Successfully fetched {len(forecasts)} day forecast for {city}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching forecast: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to fetch forecast',
                'details': str(e)
            }
    
    def clear_cache(self, city: str = None):
        """
        Clear weather cache for a specific city or all cities
        
        Args:
            city: City name (optional). If None, clears all weather cache
        """
        if city:
            cache_key = self._get_cache_key(city)
            cache.delete(cache_key)
            logger.info(f"🗑️ Cleared cache for city: {city}")
        else:
            # Clear all weather-related cache
            cache.clear()
            logger.info("🗑️ Cleared all weather cache")