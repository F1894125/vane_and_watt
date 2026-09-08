import numpy as np
import pandas as pd
import tensorflow as tf
from joblib import load
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import (
    WeatherPrediction, EnergyPrediction
)


# Loading models at the task level or module level
# is increasing latency as every prediction request
# or terminal command is reloading the models and
# scalers, which are bulky

# Artifacts should be loaded lazily to prevent this

WEATHER_X_SCALER = None
WEATHER_Y_SCALER = None
WEATHER_MODEL = None
LOAD_MODEL = None
GEN_MODEL = None


def get_weather_scalers():
    """Lazy-loads and caches the weather scalers."""
    global WEATHER_X_SCALER, WEATHER_Y_SCALER

    if WEATHER_X_SCALER is None:
        WEATHER_X_SCALER = load(settings.WEATHER_X_SCALER)
    if WEATHER_Y_SCALER is None:
        WEATHER_Y_SCALER = load(settings.WEATHER_Y_SCALER)

    return WEATHER_X_SCALER, WEATHER_Y_SCALER


def get_weather_model():
    """Lazy-loads and caches the Keras LSTM model."""
    global WEATHER_MODEL

    if WEATHER_MODEL is None:
        WEATHER_MODEL = tf.keras.models.load_model(
            settings.WEATHER_MODEL,
            compile=False,
        )
        WEATHER_MODEL.jit_compile = False

    return WEATHER_MODEL


def get_energy_model(category):
    """Lazy-loads and caches the appropriate XGBoost model based on category."""
    global LOAD_MODEL, GEN_MODEL

    if category == 'load':
        if LOAD_MODEL is None:
            LOAD_MODEL = load(settings.LOAD_MODEL)

        return LOAD_MODEL

    else:
        if GEN_MODEL is None:
            GEN_MODEL = load(settings.GEN_MODEL)

        return GEN_MODEL

@shared_task
def predict_weather(prediction_id: int):
    """
    Extracts the input features from the WeatherPrediction
    instance, scales them, makes a prediction, scales it
    back, and stores the prediction in the same instance
    """
    try:
        weather = WeatherPrediction.objects.get(pk=prediction_id)

        weather_X_scaler, weather_y_scaler = get_weather_scalers()
        weather_model = get_weather_model()

        weather_input = [
            weather.avg_temp_c,
            weather.min_temp_c,
            weather.max_temp_c,
            weather.avg_sea_level_pres_hpa,
            weather.avg_wind_speed_kmh,
            weather.precipitation_mm,
            weather.is_weekend,
            weather.is_raining,
            weather.sin_day_of_year,
            weather.cos_day_of_year,
            weather.sin_month,
            weather.cos_month,
            weather.sin_wind_dir,
            weather.cos_wind_dir
        ] # Have to confirm the order before building the tensor

        # Transpose to make (14, 10) to (10, 14)
        weather_input_2d = np.array(weather_input).T

        # Scale it down with X-scaler
        weather_input_scaled = weather_X_scaler.transform(weather_input_2d)

        # Reshape as a 3D tensor for LSTM (batch_size=1, lookback=10, n_features=14)
        weather_input_3d = weather_input_scaled.reshape(1, 10, 14)

        # Make prediction
        preds_scaled = weather_model.predict(weather_input_3d)

        # Getting output shape
        n_samples, horizon, n_targets = preds_scaled.shape

        # Reshaping to 2D for scaling up the predictions
        preds_scaled_2d = preds_scaled.reshape(-1, n_targets)

        # Scaling up with y-Scaler
        preds_original = weather_y_scaler.inverse_transform(preds_scaled_2d)

        # Building JSON for model instance
        target_cols = (
            'avg_temp_c', 'min_temp_c', 'max_temp_c',
            'avg_sea_level_pres_hpa', 'avg_wind_speed_kmh'
        )
        formatted_preds = []
        for day in range(horizon):
            day_pred = {
                'day': day + 1,
                'forecast': {
                    column: float(preds_original[day, index])
                    for index, column in enumerate(target_cols) 
                }
            }
            formatted_preds.append(day_pred)

        # Storing predictions in model instance
        weather.prediction = {
            'status': 'SUCCESS',
            'predictions': formatted_preds
        }
        weather.save()
    
    except Exception as e:
        weather = WeatherPrediction.objects.get(pk=prediction_id)
        weather.prediction = {
            'status': 'FAILED',
            'error': str(e)
        }
        weather.save()


@shared_task
def predict_energy(prediction_id: int):
    """
    Extracts the input features from the EnergyPrediction
    instance, selects correct XGBRegressor, makes a prediction,
    and stores the prediction in the same instance
    """
    try:
        energy = EnergyPrediction.objects.get(pk=prediction_id)
        energy_model = get_energy_model(energy.category)
        
        energy_input = pd.DataFrame([{
            'hour': energy.hour,
            'day': energy.day,
            'month': energy.month,
            'dayofweek': energy.dayofweek,
        }]) # Have to confirm the order for this one too

        if energy.category == 'load':
            energy_input['load_lag_1'] = energy.lag_1
            energy_input['load_lag_24'] = energy.lag_24
        else:
            energy_input['gen_lag_1'] = energy.lag_1
            energy_input['gen_lag_24'] = energy.lag_24
        
        # Make prediction
        preds = energy_model.predict(energy_input)
        preds = float(preds[0])
        
        # Storing predictions in model instance
        energy.prediction = {
            "status": "SUCCESS",
            "category": energy.category,
            "prediction": preds
        }
        energy.save()

        
    except Exception as e:
        energy = EnergyPrediction.objects.get(pk=prediction_id)
        energy.prediction = {
            'status': 'FAILED',
            'error': str(e)
        }
        energy.save()


@shared_task
def send_prediction_email(prediction_id, domain, user_email):
    """
    Fetches the prediction object, renders the HTML template, 
    and sends it to the user.
    """
    # Fetching the correct object based on domain
    if domain == 'weather':
        prediction = WeatherPrediction.objects.get(id=prediction_id)
    else:
        prediction = EnergyPrediction.objects.get(id=prediction_id)

    # Setting up email variables
    subject = f"Your {domain.capitalize()} Forecast Results"
    context = {
        'prediction': prediction,
        'domain': domain,
    }

    # Rendering the HTML template
    html_content = render_to_string('forecasting/prediction_email.html', context)
    text_content = "Your prediction is ready. Please view this email in an HTML-compatible client."

    # Build and send the email
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user_email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()