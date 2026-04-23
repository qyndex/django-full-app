"""DRF viewsets for the full app."""
import django.utils.timezone as timezone
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Article, Comment, Tag
from .serializers import (
    ArticleDetailSerializer,
    ArticleListSerializer,
    CommentSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    """CRUD for article tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class ArticleViewSet(viewsets.ModelViewSet):
    """CRUD for articles with publish and archive actions."""

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "body", "excerpt"]
    ordering_fields = ["created_at", "views", "published_at"]

    def get_queryset(self):
        qs = Article.objects.select_related("author").prefetch_related("tags", "comments")
        if not self.request.user.is_staff:
            qs = qs.filter(status=Article.STATUS_PUBLISHED)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ArticleListSerializer
        return ArticleDetailSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "publish", "archive"):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request: Request, pk: int | None = None) -> Response:
        article = self.get_object()
        article.status = Article.STATUS_PUBLISHED
        article.published_at = timezone.now()
        article.save(update_fields=["status", "published_at"])
        return Response({"status": "published"})

    @action(detail=True, methods=["post"])
    def archive(self, request: Request, pk: int | None = None) -> Response:
        article = self.get_object()
        article.status = Article.STATUS_ARCHIVED
        article.save(update_fields=["status"])
        return Response({"status": "archived"})

    @action(detail=True, methods=["post"], url_path="add-comment")
    def add_comment(self, request: Request, pk: int | None = None) -> Response:
        article = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(article=article, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD for comments — staff can approve."""

    queryset = Comment.objects.select_related("author", "article").all()
    serializer_class = CommentSerializer

    @action(detail=True, methods=["post"])
    def approve(self, request: Request, pk: int | None = None) -> Response:
        comment = self.get_object()
        comment.is_approved = True
        comment.save(update_fields=["is_approved"])
        return Response({"status": "approved"})
