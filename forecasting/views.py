from itertools import chain
from operator import attrgetter
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status

from .models import WeatherPrediction, EnergyPrediction
from .forms import WeatherPredictionForm, EnergyPredictionForm
from .serializers import (
    WeatherPredictionSerializer, EnergyPredictionSerializer
)
from .tasks import (
    predict_weather, predict_energy,
    send_prediction_email
)
from account.permissions import IsEntityOwner


# DRF enables rendering of templates
# and context injection using a Response
# object, and it's better than using
# FormView or TemplateView
class PredictionFormView(APIView):
    """
    View that renders both the weather
    and energy prediction forms.
    """
    permission_classes = [IsEntityOwner]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'forecasting/forecast.html'

    def get(self, request):
        weather_form = WeatherPredictionForm()
        energy_form = EnergyPredictionForm()

        return Response({
            'weather_form': weather_form,
            'energy_form': energy_form
        })
        # The response is injected into the
        # template as context.


class WeatherPredictAPIView(APIView):
    permission_classes = [IsEntityOwner]

    def post(self, request, *args, **kwargs):
        serializer = WeatherPredictionSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            weather_prediction = serializer.save()
            predict_weather.delay(weather_prediction.id)
            send_prediction_email.delay(
                weather_prediction.id, 'weather', request.user.email
            )

            return Response({
                    "message": "Weather prediction queued, redirecting to results in 3 seconds.",
                    "id": weather_prediction.id
            }, status=status.HTTP_202_ACCEPTED)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class EnergyPredictAPIView(APIView):
    permission_classes = [IsEntityOwner]

    def post(self, request, *args, **kwargs):
        serializer = EnergyPredictionSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            energy_prediction = serializer.save()
            predict_energy.delay(energy_prediction.id)
            send_prediction_email.delay(
                energy_prediction.id, 'energy', request.user.email
            )

            return Response({
                "message": "Energy prediction queued, redirecting to results in 3 seconds.",
                "id": energy_prediction.id
            }, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PredictionHistoryListView(APIView):
    """
    View that renders the prediction history
    of the user from both weather and energy
    domains.
    """
    permission_classes = [IsEntityOwner]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'forecasting/history.html'

    # Doesn't need to be atomic as it doesn't
    # mutate the state in the database
    def get(self, request):
        filter_type = request.GET.get('type', 'all')
        # Default to all if no type is passed
        user = request.user
        
        weather_qs = WeatherPrediction.objects.filter(user=user)
        energy_qs = EnergyPrediction.objects.filter(user=user)

        if filter_type == 'weather':
            queryset = weather_qs.order_by('-created_at')
        elif filter_type == 'energy':
            queryset = energy_qs.order_by('-created_at')
        else:
            queryset = sorted(
                chain(weather_qs, energy_qs),
                # As the schemas of both models are different
                # returning them together isn't possible
                # using a single queryset, so the individual
                # querysets need to be joined using chain()
                # as demonstrated in Ramalho's book
                key=attrgetter('created_at'),
                # Also, my sorting implementation to use
                # a lambda that pulls created_at from the
                # objects in the chain object is inefficient,
                # so attrgetter from the book is better
                reverse=True
            )

        paginator = Paginator(queryset, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return Response({
            'predictions': page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'filter_type': filter_type
        })


class WeatherPredictionDetailView(APIView):
    """
    View that renders the template displaying
    the prediction details made by an authenticated
    user on the weather domain.
    """
    permission_classes = [IsEntityOwner]
    # APIView doesn't implicitly check object-level
    # permissions which is why it was not working
    # correctly, so call check_object_permissions
    # explicitly to enforce object-level permissions
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'forecasting/detail.html'

    def get(self, request, pk):
        prediction = get_object_or_404(WeatherPrediction, pk=pk)
        self.check_object_permissions(request, prediction)

        return Response({
            'prediction': prediction,
            'domain': 'weather'
        })


class EnergyPredictionDetailView(APIView):
    """
    View that renders the template displaying
    the prediction details made by an authenticated
    user on the energy domain.
    """
    permission_classes = [IsEntityOwner]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'forecasting/detail.html'

    def get(self, request, pk):
        prediction = get_object_or_404(EnergyPrediction, pk=pk)
        self.check_object_permissions(request, prediction)

        return Response({
            'prediction': prediction,
            'domain': 'energy'
        })