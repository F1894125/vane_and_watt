from django.urls import path
from . import views

app_name = 'forecasting'

urlpatterns = [
    path(
        'api/prediction_form/',
        views.PredictionFormView.as_view(),
        name='prediction_form'
    ),
    path(
        'api/history/',
        views.PredictionHistoryListView.as_view(),
        name='history'
    ),
    path(
        'api/history/weather/<uuid:pk>/',
        views.WeatherPredictionDetailView.as_view(),
        name='weather_detail'
    ),
    path(
        'api/history/energy/<uuid:pk>/',
        views.EnergyPredictionDetailView.as_view(),
        name='energy_detail'
    ),
    path(
        'api/weather/predict/',
        views.WeatherPredictAPIView.as_view(),
        name='predict_weather'
    ),
    path(
        'api/energy/predict/',
        views.EnergyPredictAPIView.as_view(),
        name='predict_energy'
    ),
]