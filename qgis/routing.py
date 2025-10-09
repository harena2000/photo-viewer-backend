from django.urls import path
from .consumers import QGISConsumer

websocket_urlpatterns = [
    path("ws/qgis/", QGISConsumer.as_asgi()),
]