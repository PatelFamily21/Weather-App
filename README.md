# ☁️ Weather App - Django + Redis + Tailwind CSS

[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Redis](https://img.shields.io/badge/Redis-7.x-red.svg)](https://redis.io/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.x-38bdf8.svg)](https://tailwindcss.com/)

A modern, high-performance weather application built with Django, Redis caching, and beautiful Tailwind CSS interface. Get real-time weather information with lightning-fast response times thanks to intelligent caching.

![Weather App Screenshot](https://via.placeholder.com/800x400/667eea/ffffff?text=Weather+App+Screenshot)

## ✨ Features

- 🌤️ **Real-time Weather Data** - Current weather information from OpenWeatherMap API
- ⚡ **Lightning-Fast Caching** - Redis-powered caching with 5-minute TTL
- 📊 **Analytics Dashboard** - Track cache performance and query statistics
- 🎨 **Beautiful UI** - Modern, responsive design with Tailwind CSS
- 📱 **Mobile Friendly** - Fully responsive across all devices
- 🔒 **Secure** - CSRF protection, secure headers, and environment variables
- 📈 **Performance Metrics** - Monitor cache hit rates and response times
- 🌍 **Global Coverage** - Search weather for cities worldwide


## 🏗️ Architecture

```
┌─────────────┐
│   User/     │
│ Frontend UI │
└──────┬──────┘
       │ HTTP Request
       ▼
┌──────────────────────────────────────────┐
│         Weather API (Django)              │
│  ┌────────────────────────────────────┐  │
│  │  1. Check Redis Cache              │  │
│  │     ▼                              │  │
│  │  2. Cache Hit? ──Yes──► Return    │  │
│  │     │           Cached Data        │  │
│  │     No                             │  │
│  │     ▼                              │  │
│  │  3. Request 3rd Party API          │  │
│  │     ▼                              │  │
│  │  4. Receive API Response           │  │
│  │     ▼                              │  │
│  │  5. Save to Redis Cache            │  │
│  │     ▼                              │  │
│  │  6. Return Weather Data            │  │
│  └────────────────────────────────────┘  │
└────────┬─────────────────┬───────────────┘
         │                 │
         ▼                 ▼
    ┌─────────┐    ┌──────────────────┐
    │  Redis  │    │   3rd Party      │
    │  Cache  │    │ Weather Service  │
    │  5-min  │    │ (OpenWeatherMap) │
    └─────────┘    └──────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Django 6.0** - Python web framework
- **Python 3.12** - Programming language
- **Redis 7.x** - In-memory caching
- **django-redis** - Redis cache backend
- **requests** - HTTP library

### Frontend
- **Tailwind CSS 3.x** - Utility-first CSS framework
- **Vanilla JavaScript** - No jQuery, pure ES6+
- **Font Awesome** - Icon library

### APIs
- **OpenWeatherMap API** - Weather data provider

### Deployment
- **Gunicorn** - WSGI HTTP Server
- **WhiteNoise** - Static file serving
- **PostgreSQL** - Production database (optional)

## 📋 Prerequisites

- Python 3.12 or higher
- Redis server
- OpenWeatherMap API key (free tier available)
- Git (for version control)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/PatelFamily21/Weather-App.git
cd weather
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Start Redis

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Windows:**
Download from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)

**Verify Redis:**
```bash
redis-cli ping
# Should return: PONG
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/1

# Weather API Configuration
# Get free API key at: https://openweathermap.org/api
WEATHER_API_KEY=your-openweathermap-api-key-here
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 9. Start Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## 🧪 Testing

### Test Redis Connection

```bash
python manage.py test_weather London
```

This will:
- Test Redis connection
- Fetch weather for London
- Show cache hit/miss
- Display performance metrics

### Manual Testing

1. **Test Search**: Enter "London" and search
2. **Test Cache**: Search same city twice - see cache badge
3. **Test Statistics**: Visit `/stats/` for analytics
4. **Test About**: Visit `/about/` for architecture info

## 📊 API Endpoints

### Get Current Weather
```
GET /api/weather/?city=<city_name>
```

**Response:**
```json
{
  "success": true,
  "city": "London",
  "country": "GB",
  "temperature": 15.5,
  "feels_like": 14.2,
  "description": "Partly Cloudy",
  "humidity": 72,
  "wind_speed": 5.2,
  "from_cache": false,
  "response_time_ms": 523
}
```

### Get Weather Forecast
```
GET /api/forecast/?city=<city_name>&days=5
```

### Get Statistics
```
GET /api/stats/
```

### Clear Cache
```
POST /api/clear-cache/
POST /api/clear-cache/ (with city=London)
```

## 🎨 Customization

### Change Cache Timeout

Edit `settings.py`:
```python
WEATHER_CACHE_TIMEOUT = 300  # 5 minutes (in seconds)
```

### Change Color Scheme

Edit templates and modify Tailwind CSS classes:
```html
<!-- Change gradient -->
<body class="bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500">

<!-- Change button colors -->
<button class="bg-gradient-to-r from-purple-600 to-pink-600">
```

### Add More Quick Cities

Edit `templates/weatherapp/index.html`:
```html
<button class="quick-search-btn" data-city="Mumbai">
    <i class="fas fa-map-marker-alt mr-1"></i>Mumbai
</button>
```

## 🌐 Deployment

### Deploy to Heroku

1. **Install Heroku CLI**
2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-weather-app
   ```

4. **Add Redis Add-on**
   ```bash
   heroku addons:create heroku-redis:mini
   ```

5. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set WEATHER_API_KEY=your-api-key
   ```

6. **Deploy**
   ```bash
   git push heroku main
   ```

7. **Run Migrations**
   ```bash
   heroku run python manage.py migrate
   ```

### Deploy to Railway

1. **Connect GitHub Repository**
2. **Add Environment Variables**
   - `SECRET_KEY`
   - `WEATHER_API_KEY`
   - `REDIS_URL` (Railway provides this)
3. **Deploy automatically on push**

### Deploy to Render

1. **Connect GitHub Repository**
2. **Add Redis Service**
3. **Configure Environment Variables**
4. **Deploy**

## 📁 Project Structure

```
weather-app/
├── weather/                    # Django project settings
│   ├── settings.py            # Main settings
│   ├── urls.py                # URL configuration
│   └── wsgi.py                # WSGI application
├── weatherapp/                # Main application
│   ├── models.py              # Database models
│   ├── views.py               # Views and API endpoints
│   ├── services.py            # Weather service with caching
│   ├── urls.py                # App URLs
│   ├── admin.py               # Admin configuration
│   └── templatetags/          # Custom template filters
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   └── weatherapp/
│       ├── index.html        # Main page
│       ├── stats.html        # Statistics page
│       └── about.html        # About page
├── static/                    # Static files
│   └── js/
│       └── weather.js        # Frontend JavaScript
├── staticfiles/               # Collected static files
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
├── Procfile                  # Deployment configuration
├── runtime.txt               # Python version
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Django secret key | - | Yes |
| `DEBUG` | Debug mode | `False` | No |
| `ALLOWED_HOSTS` | Allowed hosts | `*` | Production |
| `DATABASE_URL` | PostgreSQL URL | SQLite | Production |
| `REDIS_URL` | Redis connection URL | `redis://127.0.0.1:6379/1` | Yes |
| `WEATHER_API_KEY` | OpenWeatherMap API key | - | Yes |

### Cache Configuration

- **Cache Backend**: Redis
- **Cache Timeout**: 5 minutes (300 seconds)
- **Cache Key Prefix**: `weather:`
- **Cache Key Format**: `weather:weather_data_{city}`

## 📈 Performance

### Cache Benefits

- **Response Time**: ~50ms (cached) vs ~500-1000ms (API call)
- **API Call Reduction**: 80-90% for popular cities
- **Cost Savings**: Significant reduction in API usage
- **User Experience**: Much faster loading times

### Benchmarks

| Metric | Without Cache | With Cache | Improvement |
|--------|---------------|------------|-------------|
| Response Time | ~500-1000ms | ~50ms | 10-20x faster |
| API Calls | 100% | 10-20% | 80-90% reduction |
| Cache Hit Rate | 0% | 80-90% | N/A |

## 🐛 Troubleshooting

### Redis Connection Error

```bash
# Check if Redis is running
redis-cli ping

# Start Redis if not running
sudo systemctl start redis-server  # Linux
brew services start redis           # macOS
```

### Invalid API Key

- Check your `.env` file
- Verify API key at https://openweathermap.org/api
- Wait a few minutes after generating (activation time)

### City Not Found

- Check spelling
- Use English city names
- Try major cities first

### Static Files Not Loading

```bash
python manage.py collectstatic --noinput
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Your Name**

- GitHub: [Patel Hadaisa](https://github.com/PatelFamily21)


## 🙏 Acknowledgments

- [OpenWeatherMap](https://openweathermap.org/) for the weather API
- [Django](https://www.djangoproject.com/) for the amazing web framework
- [Redis](https://redis.io/) for the fast caching solution
- [Tailwind CSS](https://tailwindcss.com/) for the beautiful UI framework
- [Font Awesome](https://fontawesome.com/) for the icons

## 📧 Support

If you have any questions or issues, please open an issue on GitHub or contact me directly.

---

**Built with ❤️ using Django, Redis, and Tailwind CSS**

⭐ Star this repo if you found it helpful!
