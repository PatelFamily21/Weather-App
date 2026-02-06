"""
Enhanced Geolocation Service - Better location accuracy
Uses multiple strategies to find the closest city/town
"""
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EnhancedGeolocationService:
    """
    Enhanced service to get precise city/town names from coordinates
    Uses multiple data sources for better accuracy
    """
    
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/geo/1.0"
    
    def get_precise_location(self, latitude: float, longitude: float) -> dict:
        """
        Get precise location using multiple strategies
        
        Strategy:
        1. Try OpenStreetMap Nominatim (very detailed, includes towns/suburbs)
        2. Fall back to OpenWeatherMap reverse geocoding
        3. Try to find nearest weather station
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            dict: Detailed location information
        """
        # Strategy 1: OpenStreetMap Nominatim (Free, very detailed)
        osm_result = self._get_location_from_nominatim(latitude, longitude)
        if osm_result.get('success'):
            logger.info(f"✅ Found precise location via OSM: {osm_result.get('display_name')}")
            return osm_result
        
        # Strategy 2: OpenWeatherMap (Fallback)
        owm_result = self._get_location_from_openweather(latitude, longitude)
        if owm_result.get('success'):
            logger.info(f"✅ Found location via OWM: {owm_result.get('city')}")
            return owm_result
        
        # Strategy 3: Try to get nearest city from weather API
        nearest_result = self._find_nearest_weather_station(latitude, longitude)
        if nearest_result.get('success'):
            logger.info(f"✅ Found nearest weather station: {nearest_result.get('city')}")
            return nearest_result
        
        return {
            'success': False,
            'error': 'Could not determine location',
            'details': 'Unable to find city/town for these coordinates'
        }
    
    def _get_location_from_nominatim(self, latitude: float, longitude: float) -> dict:
        """
        Get location from OpenStreetMap Nominatim API
        This provides very detailed location data including suburbs, towns, villages
        
        FREE and more accurate for precise locations!
        """
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'addressdetails': 1,
            'zoom': 14,  # Level of detail (14 = suburb/town level)
        }
        headers = {
            'User-Agent': 'WeatherApp/1.0'  # Required by Nominatim
        }
        
        try:
            logger.info(f"🔍 Querying OpenStreetMap for {latitude}, {longitude}")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and 'address' in data:
                address = data['address']
                
                # Try to get the most specific location available
                # Priority: suburb > town > city > county > state
                city = (
                    address.get('suburb') or 
                    address.get('neighbourhood') or
                    address.get('town') or 
                    address.get('city') or 
                    address.get('municipality') or
                    address.get('county') or
                    address.get('state')
                )
                
                # Get additional details
                state = address.get('state', '')
                country = address.get('country', '')
                country_code = address.get('country_code', '').upper()
                
                result = {
                    'success': True,
                    'city': city,
                    'suburb': address.get('suburb', ''),
                    'town': address.get('town', ''),
                    'city_district': address.get('city_district', ''),
                    'state': state,
                    'country': country,
                    'country_code': country_code,
                    'latitude': float(data.get('lat', latitude)),
                    'longitude': float(data.get('lon', longitude)),
                    'display_name': data.get('display_name', ''),
                    'source': 'OpenStreetMap',
                    'accuracy': 'high'
                }
                
                logger.info(f"📍 OSM Result: {city}, {state}, {country}")
                return result
            else:
                logger.warning("⚠️ No address data from Nominatim")
                return {'success': False}
                
        except requests.exceptions.Timeout:
            logger.warning("⏱️ Nominatim request timeout")
            return {'success': False}
        except Exception as e:
            logger.error(f"❌ Nominatim error: {str(e)}")
            return {'success': False}
    
    def _get_location_from_openweather(self, latitude: float, longitude: float) -> dict:
        """
        Fallback: Get location from OpenWeatherMap reverse geocoding
        """
        url = f"{self.base_url}/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'limit': 5,  # Get multiple results to find closest
            'appid': self.api_key
        }
        
        try:
            logger.info(f"🔍 Querying OpenWeatherMap for {latitude}, {longitude}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                # Get the first result (closest)
                location = data[0]
                
                result = {
                    'success': True,
                    'city': location.get('name'),
                    'state': location.get('state', ''),
                    'country': location.get('country'),
                    'country_code': location.get('country'),
                    'latitude': location.get('lat'),
                    'longitude': location.get('lon'),
                    'source': 'OpenWeatherMap',
                    'accuracy': 'medium'
                }
                
                logger.info(f"📍 OWM Result: {result['city']}, {result['country']}")
                return result
            else:
                return {'success': False}
                
        except Exception as e:
            logger.error(f"❌ OpenWeatherMap reverse geocoding error: {str(e)}")
            return {'success': False}
    
    def _find_nearest_weather_station(self, latitude: float, longitude: float) -> dict:
        """
        Find nearest weather station/city with weather data
        Uses the 'find' endpoint from OpenWeatherMap
        """
        url = "https://api.openweathermap.org/data/2.5/find"
        params = {
            'lat': latitude,
            'lon': longitude,
            'cnt': 10,  # Get 10 nearest cities
            'appid': self.api_key
        }
        
        try:
            logger.info(f"🔍 Finding nearest weather stations for {latitude}, {longitude}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and 'list' in data and len(data['list']) > 0:
                # Get the closest city
                closest = data['list'][0]
                
                result = {
                    'success': True,
                    'city': closest.get('name'),
                    'country': closest.get('sys', {}).get('country'),
                    'latitude': closest.get('coord', {}).get('lat'),
                    'longitude': closest.get('coord', {}).get('lon'),
                    'distance': self._calculate_distance(
                        latitude, longitude,
                        closest.get('coord', {}).get('lat'),
                        closest.get('coord', {}).get('lon')
                    ),
                    'source': 'Weather Stations',
                    'accuracy': 'medium'
                }
                
                logger.info(f"📍 Nearest station: {result['city']}, {result['country']} ({result['distance']:.1f}km)")
                return result
            else:
                return {'success': False}
                
        except Exception as e:
            logger.error(f"❌ Weather station search error: {str(e)}")
            return {'success': False}
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates in kilometers
        Using Haversine formula
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return distance
    
    def get_nearby_cities(self, latitude: float, longitude: float, radius: int = 50) -> dict:
        """
        Get all cities within a radius (in kilometers)
        Useful for showing user options if exact location doesn't have weather data
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in kilometers (default 50km)
            
        Returns:
            dict: List of nearby cities
        """
        url = "https://api.openweathermap.org/data/2.5/find"
        params = {
            'lat': latitude,
            'lon': longitude,
            'cnt': 50,  # Get up to 50 cities
            'appid': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            cities = []
            if data and 'list' in data:
                for city in data['list']:
                    city_lat = city.get('coord', {}).get('lat')
                    city_lon = city.get('coord', {}).get('lon')
                    
                    distance = self._calculate_distance(
                        latitude, longitude, city_lat, city_lon
                    )
                    
                    # Only include cities within radius
                    if distance <= radius:
                        cities.append({
                            'city': city.get('name'),
                            'country': city.get('sys', {}).get('country'),
                            'latitude': city_lat,
                            'longitude': city_lon,
                            'distance': round(distance, 1)
                        })
                
                # Sort by distance
                cities.sort(key=lambda x: x['distance'])
                
                logger.info(f"✅ Found {len(cities)} cities within {radius}km")
                return {
                    'success': True,
                    'cities': cities,
                    'count': len(cities),
                    'radius': radius
                }
            else:
                return {
                    'success': False,
                    'error': 'No nearby cities found'
                }
                
        except Exception as e:
            logger.error(f"❌ Nearby cities search error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to find nearby cities',
                'details': str(e)
            }