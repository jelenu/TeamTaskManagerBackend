from django.urls import re_path
from .consumers.consumers import BoardConsumer, NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/board/(?P<board_id>\d+)/$', BoardConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]
