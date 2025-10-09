from django.urls import re_path
from .consumers import QGISLayerConsumer

websocket_urlpatterns = [
    re_path(r"^ws/qgis/$", QGISLayerConsumer.as_asgi()),
]