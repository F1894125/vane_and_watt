from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from forecasting.models import WeatherPrediction, EnergyPrediction

User = get_user_model()

class ForecastingModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester', 
            password='secretpassword'
        )

    def test_energy_prediction_get_absolute_url(self):
        """Test to check if the canonical URL returns correctly for Energy domain."""
        prediction = EnergyPrediction.objects.create(
            user=self.user,
            category=EnergyPrediction.EnergyCategory.LOAD,
            hour=12, day=1, month=1, dayofweek=1,
            lag_1=100.0, lag_24=105.0
        )
        expected_url = reverse('forecasting:energy_detail', kwargs={'pk': prediction.pk})
        self.assertEqual(prediction.get_absolute_url(), expected_url)

    def test_weather_prediction_get_absolute_url(self):
        """Test to check if the canonical URL returns correctly for Weather domain."""
        # Generating dummy arrays of size 10 to satisfy the ArrayFields
        zeros = [0.0] * 10
        int_zeros = [0] * 10
        
        prediction = WeatherPrediction.objects.create(
            user=self.user,
            precipitation_mm=zeros,
            is_weekend=int_zeros,
            is_raining=int_zeros,
            sin_day_of_year=zeros, cos_day_of_year=zeros,
            sin_month=zeros, cos_month=zeros,
            sin_wind_dir=zeros, cos_wind_dir=zeros,
            avg_temp_c=zeros, min_temp_c=zeros, max_temp_c=zeros,
            avg_sea_level_pres_hpa=zeros, avg_wind_speed_kmh=zeros
        )
        expected_url = reverse('forecasting:weather_detail', kwargs={'pk': prediction.pk})
        self.assertEqual(prediction.get_absolute_url(), expected_url)