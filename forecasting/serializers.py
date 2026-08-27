from rest_framework import serializers
from .models import WeatherPrediction, EnergyPrediction

class WeatherPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherPrediction
        fields = (
            'precipitation_mm', 'is_weekend',
            'is_raining', 'sin_day_of_year',
            'cos_day_of_year', 'sin_month',
            'cos_month', 'sin_wind_dir',
            'cos_wind_dir', 'avg_temp_c',
            'min_temp_c', 'max_temp_c',
            'avg_sea_level_pres_hpa',
            'avg_wind_speed_kmh',
        )

    def create(self, validated_data):
        """Creates a WeatherPrediction instance."""
        prediction = (
            WeatherPrediction
            .objects.create(
                **validated_data,
                user=self.context['request'].user
            )
        )

        return prediction
    
class EnergyPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyPrediction
        fields = (
            'category', 'hour', 'day',
            'month', 'dayofweek', 'lag_1',
            'lag_24',
        )

    def create(self, validated_data):
        """Creates a EnergyPrediction instance."""
        prediction = (
            EnergyPrediction
            .objects.create(
                **validated_data,
                user=self.context['request'].user
            )
        )

        return prediction