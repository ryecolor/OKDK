"""
ASGI config for OKDK project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from connection import routing as connection_routing
from alerts import routing as alerts_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OKDK.settings')

# 모든 웹소켓 패턴을 하나의 리스트로 결합
websocket_urlpatterns = [
    *connection_routing.websocket_urlpatterns,
    *alerts_routing.websocket_urlpatterns
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
