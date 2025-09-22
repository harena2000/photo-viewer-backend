from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/", include("authentification.urls")),
    path("api/explorer/", include("explorer.urls"))
]
