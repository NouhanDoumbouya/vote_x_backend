import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Import WebSocket routing modules
import votes.routing
import polls.routing

# Set correct Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vote_x_backend.settings")

# ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            votes.routing.websocket_urlpatterns + polls.routing.websocket_urlpatterns
        )
    ),
})
