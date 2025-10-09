from django.urls import path
from .views import update_layers, get_layers

urlpatterns = [
    path("update_layers/", update_layers),
    path("get_layers/", get_layers),
]