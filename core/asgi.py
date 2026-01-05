import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from bids.routing import websocket_urlpatterns



application = ProtocolTypeRouter({
    "http": django_asgi_app, # Handles standard requests
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns) # Handles WebSockets
    ),
})