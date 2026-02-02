"""
Weather App Models
Stores weather query history and analytics
"""
from django.db import models
from django.utils import timezone


class WeatherQuery(models.Model):
    """
    Model to track weather queries for analytics and history
    """
    city = models.CharField(max_length=100, db_index=True)
    country = models.CharField(max_length=10, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=200, blank=True)
    query_time = models.DateTimeField(auto_now_add=True, db_index=True)
    from_cache = models.BooleanField(default=False)
    response_time_ms = models.IntegerField(null=True, blank=True, help_text="Response time in milliseconds")
    
    class Meta:
        ordering = ['-query_time']
        verbose_name = 'Weather Query'
        verbose_name_plural = 'Weather Queries'
        indexes = [
            models.Index(fields=['-query_time']),
            models.Index(fields=['city', '-query_time']),
        ]
    
    def __str__(self):
        return f"{self.city} - {self.query_time.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def cache_status(self):
        """Return user-friendly cache status"""
        return "Cached" if self.from_cache else "Fresh API Call"


class FavoriteCity(models.Model):
    """
    Model to store favorite cities (optional feature for future enhancement)
    """
    city = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=10, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)
    query_count = models.IntegerField(default=0)
    last_queried = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-query_count', 'city']
        verbose_name = 'Favorite City'
        verbose_name_plural = 'Favorite Cities'
    
    def __str__(self):
        return f"{self.city} ({self.query_count} queries)"
    
    def increment_query_count(self):
        """Increment the query count and update last queried time"""
        self.query_count += 1
        self.last_queried = timezone.now()
        self.save()


class WeatherAlert(models.Model):
    """
    Model to store weather alerts (optional feature for future enhancement)
    """
    ALERT_TYPES = [
        ('rain', 'Rain'),
        ('storm', 'Storm'),
        ('snow', 'Snow'),
        ('heat', 'Extreme Heat'),
        ('cold', 'Extreme Cold'),
        ('wind', 'High Wind'),
    ]
    
    city = models.CharField(max_length=100)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    severity = models.IntegerField(default=1, help_text="1=Low, 2=Medium, 3=High")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-severity', '-created_at']
        verbose_name = 'Weather Alert'
        verbose_name_plural = 'Weather Alerts'
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.city}"
    
    @property
    def is_expired(self):
        """Check if alert has expired"""
        return timezone.now() > self.expires_at