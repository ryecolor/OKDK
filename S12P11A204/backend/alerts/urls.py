# alerts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('weather/', views.get_weather, name='get_weather'),
    path('weather/initialize/', views.initialize_weather_data, name='initialize_weather'),
]
