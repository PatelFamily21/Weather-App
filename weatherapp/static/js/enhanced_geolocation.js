/**
 * ENHANCED Geolocation Feature - Better Accuracy
 * Replace your existing geolocation.js with this version
 */

// ===================================================================
// ENHANCED GEOLOCATION FUNCTIONALITY
// ===================================================================

/**
 * Get user's precise location and fetch weather
 * Now shows suburb/town/city district information
 */
async function getWeatherForCurrentLocation() {
    const btn = document.getElementById('locationBtn');
    const btnText = document.getElementById('locationBtnText');
    const btnIcon = document.getElementById('locationBtnIcon');
    
    if (!navigator.geolocation) {
        showError('Geolocation not supported', 'Your browser does not support location detection');
        return;
    }
    
    // Show loading state
    if (btn) {
        btn.disabled = true;
        btnText.textContent = 'Detecting...';
        btnIcon.className = 'fas fa-spinner fa-spin';
    }
    
    // Request location with high accuracy
    navigator.geolocation.getCurrentPosition(
        // Success callback
        async (position) => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            const accuracy = position.coords.accuracy; // Accuracy in meters
            
            console.log(`📍 Location detected: ${latitude}, ${longitude}`);
            console.log(`🎯 Accuracy: ±${accuracy.toFixed(0)}m`);
            
            try {
                // Call enhanced API with show_nearby option
                const response = await fetch(
                    `/api/weather/coordinates/?lat=${latitude}&lon=${longitude}&show_nearby=true`
                );
                const data = await response.json();
                
                if (btn) {
                    btn.disabled = false;
                    btnText.textContent = 'Use My Location';
                    btnIcon.className = 'fas fa-location-arrow';
                }
                
                if (data.success) {
                    // Show detailed location information
                    let locationText = data.city;
                    
                    // Add suburb/district if available
                    if (data.suburb && data.suburb !== data.city) {
                        locationText = `${data.suburb}, ${data.city}`;
                    }
                    
                    // Add state if available
                    if (data.state) {
                        locationText += `, ${data.state}`;
                    }
                    
                    // Update city input with precise location
                    document.getElementById('cityInput').value = data.city;
                    
                    // Display weather
                    displayWeather(data);
                    
                    // Show detailed success message
                    let successMsg = `📍 Weather loaded for: ${locationText}`;
                    
                    // Add accuracy information
                    if (data.detection_accuracy) {
                        const accuracyEmoji = data.detection_accuracy === 'high' ? '🎯' : '📌';
                        successMsg += `\n${accuracyEmoji} Detection: ${data.detection_accuracy} accuracy`;
                    }
                    
                    // Add source information
                    if (data.detection_source) {
                        successMsg += ` (via ${data.detection_source})`;
                    }
                    
                    showSuccessMessage(successMsg);
                    
                    // Show nearby cities if available (optional)
                    if (data.nearby_cities && data.nearby_cities.length > 0) {
                        showNearbyCitiesInfo(data.nearby_cities);
                    }
                    
                    // Save location details
                    saveDetailedLocation(data);
                    
                } else if (data.nearby_cities && data.nearby_cities.length > 0) {
                    // No exact weather data, but we have nearby options
                    showNearbyCitiesSelector(data.nearby_cities, data.location_detected);
                } else {
                    showError(data.error || 'Failed to get weather for your location', data.details);
                }
            } catch (error) {
                if (btn) {
                    btn.disabled = false;
                    btnText.textContent = 'Use My Location';
                    btnIcon.className = 'fas fa-location-arrow';
                }
                showError('Network error', 'Could not connect to the server');
                console.error('Error:', error);
            }
        },
        // Error callback
        (error) => {
            if (btn) {
                btn.disabled = false;
                btnText.textContent = 'Use My Location';
                btnIcon.className = 'fas fa-location-arrow';
            }
            
            let errorMessage = 'Could not get your location';
            let errorDetails = '';
            
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorDetails = 'Location permission denied. Please enable location access in your browser settings.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorDetails = 'Location information is unavailable. Make sure GPS is enabled.';
                    break;
                case error.TIMEOUT:
                    errorDetails = 'Location request timed out. Please try again.';
                    break;
                default:
                    errorDetails = 'An unknown error occurred.';
            }
            
            showError(errorMessage, errorDetails);
            console.error('Geolocation error:', error);
        },
        // Options - Request high accuracy
        {
            enableHighAccuracy: true,  // Use GPS if available
            timeout: 15000,            // 15 seconds timeout
            maximumAge: 60000          // 1 minute cache (fresher data)
        }
    );
}

/**
 * NEW: Show nearby cities selector when exact location has no weather data
 */
function showNearbyCitiesSelector(cities, detectedLocation) {
    const container = document.getElementById('nearbyCitiesContainer');
    
    if (!container) {
        // Create container if it doesn't exist
        const div = document.createElement('div');
        div.id = 'nearbyCitiesContainer';
        div.className = 'bg-blue-50 border-l-4 border-blue-500 p-6 rounded-lg mb-8 fade-in';
        
        const weatherResult = document.getElementById('weatherResult');
        if (weatherResult) {
            weatherResult.parentNode.insertBefore(div, weatherResult);
        }
    }
    
    const nearbyCitiesDiv = document.getElementById('nearbyCitiesContainer');
    
    nearbyCitiesDiv.innerHTML = `
        <div class="flex items-start">
            <i class="fas fa-map-marker-alt text-blue-500 text-2xl mr-4 mt-1"></i>
            <div class="flex-1">
                <h3 class="font-bold text-lg text-gray-800 mb-2">
                    📍 You're near ${detectedLocation?.city || 'this area'}
                </h3>
                <p class="text-gray-700 mb-4">
                    We don't have weather data for your exact location, but here are nearby cities:
                </p>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    ${cities.slice(0, 6).map(city => `
                        <button 
                            class="nearby-city-btn flex items-center justify-between bg-white p-3 rounded-lg border-2 border-blue-200 hover:border-blue-400 hover:bg-blue-50 transition-all text-left"
                            data-city="${city.city}"
                        >
                            <div>
                                <span class="font-semibold text-gray-800">${city.city}</span>
                                <span class="text-sm text-gray-600 block">${city.country}</span>
                            </div>
                            <div class="text-right">
                                <span class="text-sm text-blue-600 font-semibold">${city.distance}km</span>
                                <i class="fas fa-chevron-right text-blue-400 ml-2"></i>
                            </div>
                        </button>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    nearbyCitiesDiv.classList.remove('hidden');
    
    // Add click handlers
    document.querySelectorAll('.nearby-city-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const city = this.dataset.city;
            document.getElementById('cityInput').value = city;
            fetchWeather(city);
            nearbyCitiesDiv.classList.add('hidden');
        });
    });
    
    // Scroll to nearby cities
    nearbyCitiesDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * NEW: Show info about nearby cities (for reference)
 */
function showNearbyCitiesInfo(cities) {
    if (cities.length === 0) return;
    
    const infoDiv = document.getElementById('nearbyCitiesInfo');
    
    if (!infoDiv) {
        const div = document.createElement('div');
        div.id = 'nearbyCitiesInfo';
        div.className = 'mt-4 p-3 bg-white/20 rounded-lg';
        
        const weatherResult = document.getElementById('weatherResult');
        if (weatherResult) {
            weatherResult.querySelector('.weather-card').appendChild(div);
        }
    }
    
    const nearbyDiv = document.getElementById('nearbyCitiesInfo');
    
    nearbyDiv.innerHTML = `
        <p class="text-sm opacity-90 mb-2">
            <i class="fas fa-map-marked-alt mr-2"></i>
            Nearby cities (within 30km):
        </p>
        <div class="flex flex-wrap gap-2">
            ${cities.slice(0, 5).map(city => `
                <span class="text-xs bg-white/20 px-2 py-1 rounded-full">
                    ${city.city} (${city.distance}km)
                </span>
            `).join('')}
        </div>
    `;
}

/**
 * NEW: Save detailed location information
 */
function saveDetailedLocation(data) {
    const locationData = {
        city: data.city,
        suburb: data.suburb || '',
        state: data.state || '',
        country: data.country,
        lat: data.coordinates?.lat,
        lon: data.coordinates?.lon,
        accuracy: data.detection_accuracy,
        source: data.detection_source,
        timestamp: new Date().getTime()
    };
    localStorage.setItem('detailedLocation', JSON.stringify(locationData));
    
    console.log('💾 Saved detailed location:', locationData);
}

/**
 * NEW: Get detailed location from localStorage
 */
function getDetailedLocation() {
    const data = localStorage.getItem('detailedLocation');
    if (data) {
        try {
            const location = JSON.parse(data);
            const now = new Date().getTime();
            const oneHour = 60 * 60 * 1000;
            
            // Only use if less than 1 hour old
            if (now - location.timestamp < oneHour) {
                return location;
            }
        } catch (error) {
            console.error('Error parsing detailed location:', error);
        }
    }
    return null;
}

/**
 * Enhanced success message (supports multiline)
 */
function showSuccessMessage(message) {
    const successDiv = document.getElementById('successMessage');
    
    if (!successDiv) {
        const div = document.createElement('div');
        div.id = 'successMessage';
        div.className = 'hidden bg-green-100 border-l-4 border-green-500 text-green-700 p-6 rounded-lg mb-8 fade-in shadow-lg';
        div.innerHTML = `
            <div class="flex items-start">
                <i class="fas fa-check-circle text-3xl mr-4 mt-1"></i>
                <div class="flex-1">
                    <p class="font-bold text-lg">Success</p>
                    <p id="successText" class="mt-1 whitespace-pre-line"></p>
                </div>
            </div>
        `;
        
        const errorMsg = document.getElementById('errorMessage');
        if (errorMsg) {
            errorMsg.parentNode.insertBefore(div, errorMsg);
        }
    }
    
    const successElement = document.getElementById('successMessage');
    const successText = document.getElementById('successText');
    
    if (successElement && successText) {
        successText.textContent = message;
        successElement.classList.remove('hidden');
        
        // Auto-hide after 8 seconds
        setTimeout(() => {
            successElement.classList.add('hidden');
        }, 8000);
    }
}

/**
 * Check location permission and update UI
 */
async function checkLocationPermission() {
    if ('permissions' in navigator) {
        try {
            const permission = await navigator.permissions.query({ name: 'geolocation' });
            
            const locationBtn = document.getElementById('locationBtn');
            if (!locationBtn) return;
            
            updateLocationButtonStyle(permission.state);
            
            // Listen for permission changes
            permission.addEventListener('change', () => {
                updateLocationButtonStyle(permission.state);
            });
        } catch (error) {
            console.log('Permissions API not supported');
        }
    }
}

/**
 * Update location button style based on permission state
 */
function updateLocationButtonStyle(permissionState) {
    const locationBtn = document.getElementById('locationBtn');
    if (!locationBtn) return;
    
    // Remove all state classes
    locationBtn.classList.remove('bg-green-600', 'hover:bg-green-700', 
                                'bg-red-600', 'hover:bg-red-700',
                                'from-blue-600', 'to-blue-700');
    
    if (permissionState === 'granted') {
        locationBtn.classList.add('bg-green-600', 'hover:bg-green-700');
        locationBtn.title = 'Location access granted - Click to detect';
    } else if (permissionState === 'denied') {
        locationBtn.classList.add('bg-red-600', 'hover:bg-red-700');
        locationBtn.title = 'Location access denied - Enable in browser settings';
    } else {
        locationBtn.classList.add('bg-gradient-to-r', 'from-blue-600', 'to-blue-700');
        locationBtn.title = 'Get weather for your current location';
    }
}

// ===================================================================
// INITIALIZATION
// ===================================================================

document.addEventListener('DOMContentLoaded', function() {
    checkLocationPermission();
    
    const locationBtn = document.getElementById('locationBtn');
    if (locationBtn) {
        locationBtn.addEventListener('click', getWeatherForCurrentLocation);
    }
});

// Export enhanced functions
window.weatherGeo = {
    getCurrentLocation: getWeatherForCurrentLocation,
    checkPermission: checkLocationPermission,
    getDetailedLocation: getDetailedLocation,
    saveDetailedLocation: saveDetailedLocation
};