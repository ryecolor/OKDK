from django.urls import path
from . import views



urlpatterns = [
    path('start-streaming/', views.StartStreaming, name='start-streaming'),
]