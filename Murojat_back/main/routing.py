from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path("ws/chat/<int:user_id>/", ChatConsumer.as_asgi()),
    path("ws/notify/", NotificationConsumer.as_asgi()),
]
