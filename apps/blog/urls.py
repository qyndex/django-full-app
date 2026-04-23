"""URL routing for the full app — both HTML and API."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .viewsets import ArticleViewSet, CommentViewSet, TagViewSet
from .views import ArticleDetailView, ArticleListView, DashboardView

# HTML views
html_urlpatterns = [
    path("", ArticleListView.as_view(), name="article-list"),
    path("tag/<slug:tag_slug>/", ArticleListView.as_view(), name="articles-by-tag"),
    path("articles/<slug:slug>/", ArticleDetailView.as_view(), name="article-detail"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]

# REST API
router = DefaultRouter()
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"articles", ArticleViewSet, basename="article")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = html_urlpatterns + router.urls
