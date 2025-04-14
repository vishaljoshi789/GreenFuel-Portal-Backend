import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import mainapp.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "greenfuel.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # "websocket": AuthMiddlewareStack( 
    #     URLRouter(
    #         mainapp.routing.websocket_urlpatterns
    #     )
    # ),
})