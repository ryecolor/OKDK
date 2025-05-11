from django.urls import path
from . import views
from .views import VideoUploadView
from .views import VideoDownloadView


app_name = 'video'  # URL 네임스페이스를 위한 앱 이름 설정

urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    path('download/', VideoDownloadView.as_view(), name='video-download'),
    path('logdata/', views.hardware_receive, name='logdata'),
]