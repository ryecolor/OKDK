from django.urls import path
from . import views
from .views import MapConfigAPI

urlpatterns = [
    path('config/', MapConfigAPI.as_view()),
    path('drain-data/', views.get_drain_data, name='drain-data'),
]
