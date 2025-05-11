from django.urls import path
from . import views

app_name = 'region'

urlpatterns = [
    path('select-robot/', views.SelectRobotAndDrain, name='select_robot'),
    path('<int:block_id>/blockcondition/', views.block_condition, name='block_condition'),
    path('<int:block_id>/deactivate_robot/', views.deactivate_robot, name='deactivate_robot'),
    path('get_flood_images/', views.get_flood_images, name='get_flood_images'),
]
