"""
Weather app admin configuration
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import WeatherQuery, FavoriteCity, WeatherAlert


@admin.register(WeatherQuery)
class WeatherQueryAdmin(admin.ModelAdmin):
    """Admin interface for WeatherQuery model"""
    
    list_display = [
        'city', 
        'country', 
        'temperature_display', 
        'description', 
        'cache_badge',
        'response_time_display',
        'query_time'
    ]
    list_filter = [
        'from_cache', 
        'query_time',
        'country'
    ]
    search_fields = [
        'city', 
        'country', 
        'description'
    ]
    readonly_fields = [
        'query_time', 
        'response_time_ms'
    ]
    date_hierarchy = 'query_time'
    ordering = ['-query_time']
    
    def temperature_display(self, obj):
        """Display temperature with color coding"""
        if obj.temperature:
            temp = obj.temperature
            if temp >= 30:
                color = '#ff4444'  # Hot - Red
            elif temp >= 20:
                color = '#ff8800'  # Warm - Orange
            elif temp >= 10:
                color = '#00aa00'  # Mild - Green
            else:
                color = '#4444ff'  # Cold - Blue
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}°C</span>',
                color, temp
            )
        return '-'
    temperature_display.short_description = 'Temperature'
    
    def cache_badge(self, obj):
        """Display cache status with badge"""
        if obj.from_cache:
            return format_html(
                '<span style="background-color: #4caf50; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">✓ CACHED</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #2196f3; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">⚡ API CALL</span>'
            )
    cache_badge.short_description = 'Cache Status'
    
    def response_time_display(self, obj):
        """Display response time with color coding"""
        if obj.response_time_ms:
            time_ms = obj.response_time_ms
            if time_ms < 100:
                color = '#4caf50'  # Fast - Green
            elif time_ms < 500:
                color = '#ff9800'  # Medium - Orange
            else:
                color = '#f44336'  # Slow - Red
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} ms</span>',
                color, time_ms
            )
        return '-'
    response_time_display.short_description = 'Response Time'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related if needed"""
        qs = super().get_queryset(request)
        return qs


@admin.register(FavoriteCity)
class FavoriteCityAdmin(admin.ModelAdmin):
    """Admin interface for FavoriteCity model"""
    
    list_display = [
        'city',
        'country',
        'query_count_display',
        'last_queried',
        'added_date'
    ]
    list_filter = [
        'country',
        'added_date'
    ]
    search_fields = [
        'city',
        'country'
    ]
    readonly_fields = [
        'added_date',
        'query_count',
        'last_queried'
    ]
    ordering = ['-query_count', 'city']
    
    def query_count_display(self, obj):
        """Display query count with visual indicator"""
        count = obj.query_count
        if count >= 100:
            icon = '🔥🔥🔥'
        elif count >= 50:
            icon = '🔥🔥'
        elif count >= 10:
            icon = '🔥'
        else:
            icon = '📊'
        
        return format_html(
            '<span style="font-weight: bold;">{} {}</span>',
            icon, count
        )
    query_count_display.short_description = 'Queries'


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    """Admin interface for WeatherAlert model"""
    
    list_display = [
        'city',
        'alert_type',
        'severity_display',
        'is_active',
        'created_at',
        'expires_at',
        'status'
    ]
    list_filter = [
        'alert_type',
        'severity',
        'is_active',
        'created_at'
    ]
    search_fields = [
        'city',
        'message'
    ]
    readonly_fields = [
        'created_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-severity', '-created_at']
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('city', 'alert_type', 'severity')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at', 'created_at')
        }),
    )
    
    def severity_display(self, obj):
        """Display severity with color coding"""
        severity_colors = {
            1: ('#4caf50', 'Low'),
            2: ('#ff9800', 'Medium'),
            3: ('#f44336', 'High')
        }
        color, label = severity_colors.get(obj.severity, ('#9e9e9e', 'Unknown'))
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, label
        )
    severity_display.short_description = 'Severity'
    
    def status(self, obj):
        """Display alert status"""
        if obj.is_expired:
            return format_html(
                '<span style="color: #9e9e9e;">⏰ Expired</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="color: #4caf50; font-weight: bold;">✓ Active</span>'
            )
        else:
            return format_html(
                '<span style="color: #f44336;">✗ Inactive</span>'
            )
    status.short_description = 'Status'


# Customize admin site header and title
admin.site.site_header = "Weather App Administration"
admin.site.site_title = "Weather App Admin"
admin.site.index_title = "Welcome to Weather App Administration"