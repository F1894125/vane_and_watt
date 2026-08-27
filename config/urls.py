from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views
from account.views import LogoutView

urlpatterns = [
    path('admin/logout/', LogoutView.as_view(), name='admin:logout'),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('account/', include('account.urls', namespace='account')),
    path('forecasting/', include('forecasting.urls', namespace='forecasting')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
