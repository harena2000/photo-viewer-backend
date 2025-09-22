from django.urls import path
from .views import ListFiles

urlpatterns = [
    path("files/", ListFiles.as_view(), name="list_files"),
]