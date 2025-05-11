from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/video_stream/$', consumers.VideoStreamConsumer.as_asgi()),
    re_path(r'ws/json_receive/$', consumers.JSONReceiveConsumer.as_asgi()),
    re_path(r'ws/robot/$', consumers.RobotConsumer.as_asgi()),
    re_path(r'ws/drain_updates/$', consumers.DrainUpdateConsumer.as_asgi()),
]