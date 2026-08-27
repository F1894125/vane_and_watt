import uuid
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.conf import settings
from django.urls import reverse


class WeatherPrediction(models.Model):
    class BoolChoices(models.IntegerChoices):
        NO = 0, 'No'
        YES = 1, 'Yes'
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='weather_predictions'
    )

    # 14 fields for LSTM input features
    # Each field is a list of 10 values for 10 days
    precipitation_mm = ArrayField(
        models.FloatField(), size=10
    )
    is_weekend = ArrayField(models.IntegerField(
        choices=BoolChoices.choices
    ), size=10)
    is_raining = ArrayField(models.IntegerField(
        choices=BoolChoices.choices
    ), size=10)
    sin_day_of_year = ArrayField(models.FloatField(), size=10)
    cos_day_of_year = ArrayField(models.FloatField(), size=10)
    sin_month = ArrayField(models.FloatField(), size=10)
    cos_month = ArrayField(models.FloatField(), size=10)
    sin_wind_dir = ArrayField(models.FloatField(), size=10)
    cos_wind_dir = ArrayField(models.FloatField(), size=10)
    avg_temp_c = ArrayField(models.FloatField(), size=10)
    min_temp_c = ArrayField(models.FloatField(), size=10)
    max_temp_c = ArrayField(models.FloatField(), size=10)
    avg_sea_level_pres_hpa = ArrayField(models.FloatField(), size=10)
    avg_wind_speed_kmh = ArrayField(models.FloatField(), size=10)

    prediction = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        """Returns the canonical URL for a WeatherPrediction instance."""
        return reverse(
            'forecasting:weather_detail',
            kwargs={'pk': self.pk}
        )


class EnergyPrediction(models.Model):
    class EnergyCategory(models.TextChoices):
        LOAD = 'load', 'Load'
        GENERATION = 'gen', 'Generation'
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='energy_predictions'
    )
    category = models.CharField(
        max_length=4,
        choices=EnergyCategory.choices
    )

    # 6 Fields for XGBoost input features
    hour = models.IntegerField()
    day = models.IntegerField()
    month = models.IntegerField()
    dayofweek = models.IntegerField()
    lag_1 = models.FloatField()
    lag_24 = models.FloatField()

    prediction = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        """Returns the canonical URL for an EnergyPrediction instance."""
        return reverse(
            'forecasting:energy_detail',
            kwargs={'pk': self.pk}
        )