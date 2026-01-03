import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from bids.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(), # Handles standard requests
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns) # Handles WebSockets
    ),
})