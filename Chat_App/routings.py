from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from Chat.consumers import ChatConsumer
from Notification.consumers import NotificationConsumer
from Public.consumers import PublicChatConsumer

django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter({
    'http':django_asgi_app,
    'websocket':AuthMiddlewareStack(
        URLRouter([
            path('',NotificationConsumer.as_asgi()),
            path('chat/<room_id>/',ChatConsumer.as_asgi()),
            path('public_chat/<room_id>/', PublicChatConsumer.as_asgi()),
        ])
    )
})