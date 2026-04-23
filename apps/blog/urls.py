"""URL routing for the full app — both HTML and API."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .viewsets import ArticleViewSet, CategoryViewSet, CommentViewSet, TagViewSet
from .views import (
    ArticleDetailView,
    ArticleListView,
    DashboardView,
    PostCreateView,
    PostDeleteView,
    PostUpdateView,
)

# HTML views (no namespace — included at root)
html_urlpatterns = [
    path("", ArticleListView.as_view(), name="article-list"),
    path("tag/<slug:tag_slug>/", ArticleListView.as_view(), name="articles-by-tag"),
    path("category/<slug:category_slug>/", ArticleListView.as_view(), name="articles-by-category"),
    path("articles/<slug:slug>/", ArticleDetailView.as_view(), name="article-detail"),
    path("posts/new/", PostCreateView.as_view(), name="post-create"),
    path("posts/<slug:slug>/edit/", PostUpdateView.as_view(), name="post-edit"),
    path("posts/<slug:slug>/delete/", PostDeleteView.as_view(), name="post-delete"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]

# REST API (included at /api/ with namespace "api")
router = DefaultRouter()
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"articles", ArticleViewSet, basename="article")
router.register(r"comments", CommentViewSet, basename="comment")
api_urlpatterns = router.urls

# Default urlpatterns used when included without app_name
urlpatterns = html_urlpatterns
