from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Captures the bid_id as a keyword argument for the consumer
    # URL: ws://127.0.0.1:8000/ws/bid/1/
    re_path(r'ws/bid/(?P<bid_id>\d+)/$', consumers.BidConsumer.as_asgi()),
]