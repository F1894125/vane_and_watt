from django.urls import path
from . import views


app_name = 'account'

urlpatterns = [
    path(
        'api/dashboard/',
        views.DashboardView.as_view(),
        name='dashboard'
    ),
    path(
        'api/register/',
        views.RegistrationAPIView.as_view(),
        name='register'
    ),
    path(
        'api/login/',
        views.LoginAPIView.as_view(),
        name='login'
    ),
    path(
        'api/logout/',
        views.LogoutView.as_view(),
        name='logout'
    ),
    path(
        'api/profiles/<str:username>/details/',
        views.ProfileEditFormView.as_view(),
        name='profile_form'
    ),
    path(
        'api/profiles/<str:username>/',
        views.ProfileDetailAPIView.as_view(),
        name='profile_detail'
    ),
]