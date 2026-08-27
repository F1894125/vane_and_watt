from django import forms
from .models import WeatherPrediction, EnergyPrediction

class WeatherPredictionForm(forms.ModelForm):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for attribute, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': (
                    'Enter 10 comma-separated values e.g. 1.0, 2.5, 4.3, ....'
                    if attribute not in ('is_weekend', 'is_raining')
                    else 'Enter 10 comma-separated values e.g. 0, 1, 0, .... (0 = No, 1 = Yes)'
                )
            })
            # field.help_text = (
            #     "e.g. 1.0, 2.5, 4.3, ...."
            #     if attribute not in ('is_weekend', 'is_raining')
            #     else "e.g. 0, 1, 0, .... (0 = No, 1 = Yes)"
            # )


class EnergyPredictionForm(forms.ModelForm):
    class Meta:
        model = EnergyPrediction
        fields = (
            'category', 'hour', 'day',
            'month', 'dayofweek',
            'lag_1', 'lag_24',
        )
        widgets = {
            'category': forms.RadioSelect(
                attrs={'class': 'form-check-input'}
            ),
            'hour': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0', 'max': '23',
                    'step': '1'
                }
            ),
            'day': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1', 'max': '31',
                    'step': '1'
                }
            ),
            'month': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1', 'max': '12',
                    'step': '1'
                }
            ),
            'dayofweek': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0', 'max': '6',
                    'step': '1'
                }
            ),
            'lag_1': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': 'any'
                }
            ),
            'lag_24': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': 'any'
                }
            ),
        }