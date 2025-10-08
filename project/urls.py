from django.urls import path
from .views import ProjectList, ImageMetadataList

urlpatterns = [
    path("list/", ProjectList.as_view(), name="list_projects"),
    path("image/list/", ImageMetadataList.as_view(), name="list_images"),
]