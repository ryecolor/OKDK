from django.urls import path
from . import views

app_name = 'robot_info'

urlpatterns = [
    path('select-drain/', views.SelectDrain, name='select_drain'),
    path('<int:robot_id>/', views.get_robot_info, name='get_robot_info'),
    path('<int:robot_id>/get-queue/', views.get_queue, name='get_queue'),
    path('<int:robot_id>/receive_log/', views.receive_log, name='receive_log'),
]
