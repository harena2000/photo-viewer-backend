from django.urls import path
from .views import update_layers, get_layers

urlpatterns = [
    path("update-layers/", update_layers),
    path("get-layers/", get_layers),
]