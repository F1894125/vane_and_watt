from itertools import chain
from operator import attrgetter

from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import (
    TemplateHTMLRenderer, JSONRenderer
)
from rest_framework import status

from forecasting.models import WeatherPrediction, EnergyPrediction
from .forms import RegistrationForm, LoginForm, ProfileEditForm
from .models import Profile
from .permissions import IsEntityOwner
from .serializers import (
    RegistrationSerializer, ProfileSerializer, LoginSerializer
)
from .tokens import create_token


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'account/dashboard.html'

    def get(self, request):
        user = request.user
        weather_qs = WeatherPrediction.objects.filter(user=user)
        energy_qs = EnergyPrediction.objects.filter(user=user)

        weather_count = weather_qs.count()
        energy_count = energy_qs.count()
        total_count = weather_count + energy_count

        # Capping queryset to 5 most recent
        # predictions from both domains
        recent_predictions = sorted(
            chain(weather_qs, energy_qs),
            key=attrgetter('created_at'),
            reverse=True
        )[:5]

        return Response({
            'total_count': total_count,
            'weather_count': weather_count,
            'energy_count': energy_count,
            'recent_predictions': recent_predictions,
        })


class RegistrationAPIView(APIView):
    """
    Endpoint that renders the registration page and handles
    user registration.
    """
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    parser_classes = [MultiPartParser, FormParser]
    template_name = 'account/register.html'

    def dispatch(self, request, *args, **kwargs):
        """Redirect already-authenticated users to dashboard."""
        if request.user.is_authenticated:
            return redirect('account:dashboard')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Render the registration form."""
        return Response(
            {'form': RegistrationForm()},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Validate registration data and create a new user."""
        serializer = RegistrationSerializer(
            data=request.data,
            context={'request': request},
        )

        if not serializer.is_valid():
            return Response({
                'error': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({
            'detail': 'Registration successful.'
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """
    API endpoint that allows a user to log in.
    """
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'account/login.html'

    def dispatch(self, request, *args, **kwargs):
        """Redirect already-authenticated users to home."""
        if request.user.is_authenticated:
            return redirect('account:dashboard')
        
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Render the login form."""
        login_form = LoginForm()

        return Response(
            {'form': login_form},
            status=status.HTTP_200_OK
        )

    def post(self, request):
        """Authenticate a user and set tokens in cookies."""
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
            # request is passed as context as
            # serializers don't inherently know
            # which request's data it is processing
        )
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.validated_data['user']
        
        access_token = create_token(user.id, 'a')
        refresh_token = create_token(user.id, 'r')

        response = Response(
            {'detail': 'Login successful.'},
            status=status.HTTP_200_OK
        )

        response.set_cookie(
            key='access_token', value=access_token,
            httponly=True, samesite='Lax'
        )
        response.set_cookie(
            key='refresh_token', value=refresh_token,
            httponly=True, samesite='Lax'
        )

        return response


class LogoutView(APIView):
    """
    API View that logs a user out of both
    the admin panel and the site, clearing tokens and session.
    """
    def get(self, request, *args, **kwargs):
        logout(request)
        
        # Redirect back to login form and clear cookie tokens
        response = redirect(reverse("account:login"))
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class ProfileEditFormView(APIView):
    """
    Renders the Edit Profile HTML page
    with a pre-populated form.
    """
    permission_classes = [IsEntityOwner]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'account/edit_profile.html'

    def get(self, request, username):
        profile = get_object_or_404(Profile.objects.select_related('user'), user__username=username)
        self.check_object_permissions(request, profile)

        initial_data = {
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'username': profile.user.username,
            'email': profile.user.email,
            'date_of_birth': profile.date_of_birth,
        }
        form = ProfileEditForm(initial=initial_data)

        return Response({
            'form': form,
            'profile': profile,
        })

class ProfileDetailAPIView(RetrieveUpdateAPIView):
    """
    API endpoint that returns a user's profile
    information and allows them to update it.
    """
    queryset = Profile.objects.select_related('user')
    serializer_class = ProfileSerializer
    permission_classes = [IsEntityOwner]
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'