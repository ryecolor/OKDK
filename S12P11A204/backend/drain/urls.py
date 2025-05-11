from django.urls import path
from .views import BlockDrainListView
from . import views

urlpatterns = [
    path('<int:block_id>/drains/', BlockDrainListView.as_view(), name='block-drains'),
    path('<int:block_id>/selected_robot/', views.selected_robot, name='selected_robot'),
    path('<int:block_id>/receive-img/<int:drain_id>/', views.receive_img, name='receive_img'),
    path('<int:block_id>/<int:drain_id>/draincondition/', views.drain_condition, name='drain_condition'),
    path('<int:block_id>/<int:drain_id>/<int:draincondition_id>/state-correction/', views.state_correction, name='state-correction'),
    path('<int:block_id>/<int:drain_id>/latest-image/', views.get_latest_image, name='get_latest_image'),
]
