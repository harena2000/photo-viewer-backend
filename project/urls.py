from django.urls import path
from .views import ProjectList

urlpatterns = [
    path("project/", ProjectList.as_view(), name="list_files"),
]