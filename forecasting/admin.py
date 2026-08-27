from django.contrib import admin
from .models import WeatherPrediction, EnergyPrediction


@admin.register(WeatherPrediction)
class WeatherPredictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at',)
    list_filter = ('created_at', 'user')
    search_fields = ('id', 'user__username', 'user__email')
    readonly_fields = ('id', 'created_at', 'prediction')


@admin.register(EnergyPrediction)
class EnergyPredictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'category')
    list_filter = ('created_at', 'user')
    search_fields = ('id', 'user__username', 'user__email')
    readonly_fields = ('id', 'created_at', 'prediction')