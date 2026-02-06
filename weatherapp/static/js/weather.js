/**
 * Weather App Frontend JavaScript
 * Handles API calls to Django backend and UI updates
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('weatherForm');
    const cityInput = document.getElementById('cityInput');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const weatherResult = document.getElementById('weatherResult');
    const cacheBadge = document.getElementById('cacheBadge');
    const responseTimeBadge = document.getElementById('responseTimeBadge');

    // Get CSRF token from Django
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const city = cityInput.value.trim();
        
        if (!city) {
            showError('Please enter a city name');
            return;
        }

        await fetchWeather(city);
    });

    /**
     * Fetch weather data from Django API
     */
    async function fetchWeather(city) {
        // Show loading, hide others
        loading.classList.remove('hidden');
        errorMessage.classList.add('hidden');
        weatherResult.classList.add('hidden');

        try {
            // Call Django API endpoint
            const response = await fetch(`/api/weather/?city=${encodeURIComponent(city)}`);
            const data = await response.json();

            loading.classList.add('hidden');

            if (data.success) {
                displayWeather(data);
            } else {
                showError(data.error || 'Failed to fetch weather data', data.details);
            }
        } catch (error) {
            loading.classList.add('hidden');
            showError('Network error: Could not connect to the server');
            console.error('Error:', error);
        }
    }

    /**
     * Display weather data in the UI
     */
    function displayWeather(data) {
        // Show cache badge if data is from cache
        if (data.from_cache) {
            cacheBadge.classList.remove('hidden');
        } else {
            cacheBadge.classList.add('hidden');
        }

        // Show response time
        if (data.response_time_ms) {
            responseTimeBadge.classList.remove('hidden');
            document.getElementById('responseTime').textContent = `${data.response_time_ms}ms`;
        } else {
            responseTimeBadge.classList.add('hidden');
        }

        const locationBadge = document.getElementById('locationBadge');
        if (locationBadge && data.location_detected) {
            locationBadge.classList.remove('hidden');
        } else if (locationBadge) {
        locationBadge.classList.add('hidden');
        }

        // Update main weather information
        document.getElementById('cityName').textContent = `${data.city}, ${data.country}`;
        document.getElementById('weatherDesc').textContent = data.description;
        document.getElementById('temperature').textContent = `${data.temperature}°C`;
        document.getElementById('feelsLike').textContent = `${data.feels_like}°C`;
        
        // Temperature range
        if (data.temp_min && data.temp_max) {
            document.getElementById('tempRange').textContent = `${data.temp_min}°C - ${data.temp_max}°C`;
        }

        // Weather details
        document.getElementById('humidity').textContent = data.humidity;
        document.getElementById('windSpeed').textContent = data.wind_speed;
        document.getElementById('pressure').textContent = data.pressure;
        document.getElementById('clouds').textContent = data.clouds;
        document.getElementById('windDeg').textContent = data.wind_deg;
        
        // Visibility (convert from meters to kilometers)
        const visibilityKm = (data.visibility / 1000).toFixed(1);
        document.getElementById('visibility').textContent = visibilityKm;

        // Update weather icon
        const iconUrl = `https://openweathermap.org/img/wn/${data.icon}@4x.png`;
        document.getElementById('weatherIcon').src = iconUrl;

        // Format and display sunrise/sunset times
        if (data.sunrise) {
            const sunriseTime = new Date(data.sunrise * 1000);
            document.getElementById('sunrise').textContent = formatTime(sunriseTime);
        }
        if (data.sunset) {
            const sunsetTime = new Date(data.sunset * 1000);
            document.getElementById('sunset').textContent = formatTime(sunsetTime);
        }

        // Display coordinates
        if (data.coord) {
            document.getElementById('coordinates').textContent = 
                `${data.coord.lat.toFixed(2)}°N, ${data.coord.lon.toFixed(2)}°E`;
        }

        // Show weather result with animation
        weatherResult.classList.remove('hidden');
        
        // Smooth scroll to results
        weatherResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    }

    /**
     * Format time from Date object
     */
    function formatTime(date) {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }

    /**
     * Display error message
     */
    function showError(message, details) {
        let errorMsg = message;
        if (details) {
            errorMsg += `<br><small class="opacity-75">${details}</small>`;
        }
        errorText.innerHTML = errorMsg;
        errorMessage.classList.remove('hidden');
        weatherResult.classList.add('hidden');
        
        // Auto-hide error after 5 seconds
        setTimeout(() => {
            errorMessage.classList.add('hidden');
        }, 5000);
        
        // Scroll to error
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Auto-focus on city input
    cityInput.focus();

    // Add some popular cities as rotating placeholder suggestions
    const popularCities = ['Nairobi', 'London', 'New York', 'Tokyo', 'Paris', 'Dubai', 'Sydney', 'Mumbai'];
    let currentSuggestionIndex = 0;

    // Rotate placeholder suggestions every 3 seconds
    setInterval(() => {
        currentSuggestionIndex = (currentSuggestionIndex + 1) % popularCities.length;
        cityInput.placeholder = `Enter city name (e.g., ${popularCities[currentSuggestionIndex]})`;
    }, 3000);

    // Add keyboard shortcut: Press '/' to focus search
    document.addEventListener('keydown', function(e) {
        if (e.key === '/' && document.activeElement !== cityInput) {
            e.preventDefault();
            cityInput.focus();
        }
    });

    // Enable Enter key on quick search buttons
    document.querySelectorAll('.quick-search-btn').forEach(btn => {
        btn.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                this.click();
            }
        });
    });
});

/**
 * Format timestamp to readable date/time
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Get weather emoji based on weather condition
 */
function getWeatherEmoji(icon) {
    const iconMap = {
        '01d': '☀️',  // clear sky day
        '01n': '🌙',  // clear sky night
        '02d': '⛅',  // few clouds day
        '02n': '☁️',  // few clouds night
        '03d': '☁️',  // scattered clouds
        '03n': '☁️',
        '04d': '☁️',  // broken clouds
        '04n': '☁️',
        '09d': '🌧️',  // shower rain
        '09n': '🌧️',
        '10d': '🌦️',  // rain day
        '10n': '🌧️',  // rain night
        '11d': '⛈️',  // thunderstorm
        '11n': '⛈️',
        '13d': '❄️',  // snow
        '13n': '❄️',
        '50d': '🌫️',  // mist
        '50n': '🌫️'
    };
    return iconMap[icon] || '🌤️';
}

/*
// Update displayWeather function to handle location badge
function displayWeather(data) {
    // ... existing code ...
    
    // NEW: Show location badge if detected from GPS
    const locationBadge = document.getElementById('locationBadge');
    if (locationBadge && data.location_detected) {
        locationBadge.classList.remove('hidden');
    } else if (locationBadge) {
        locationBadge.classList.add('hidden');
    }
    
    // ... rest of existing code ...
} */