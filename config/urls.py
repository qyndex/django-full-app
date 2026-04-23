"""Root URL configuration for the full app."""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(("apps.blog.urls", "api"), namespace="api")),
    path("", include("apps.blog.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
