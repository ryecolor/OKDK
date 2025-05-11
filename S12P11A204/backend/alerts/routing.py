# alerts/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'api/socket/alerts/$', consumers.AlertConsumer.as_asgi()),  # 경로 변경
]