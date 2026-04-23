"""DRF viewsets for the blog API."""
import django.utils.timezone as timezone
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Category, Comment, Post, Tag
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    PostDetailSerializer,
    PostListSerializer,
    TagSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD for categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class TagViewSet(viewsets.ModelViewSet):
    """CRUD for article tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class ArticleViewSet(viewsets.ModelViewSet):
    """CRUD for posts with publish and archive actions."""

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content", "excerpt"]
    ordering_fields = ["created_at", "views", "published_at"]

    def get_queryset(self):
        qs = Post.objects.select_related("author", "category").prefetch_related("tags", "comments")
        if not self.request.user.is_staff:
            qs = qs.filter(status=Post.STATUS_PUBLISHED)
        category_slug = self.request.query_params.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostDetailSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "publish", "archive"):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request: Request, pk=None) -> Response:
        post = self.get_object()
        post.status = Post.STATUS_PUBLISHED
        post.published_at = timezone.now()
        post.save(update_fields=["status", "published_at"])
        return Response({"status": "published"})

    @action(detail=True, methods=["post"])
    def archive(self, request: Request, pk=None) -> Response:
        post = self.get_object()
        post.status = Post.STATUS_ARCHIVED
        post.save(update_fields=["status"])
        return Response({"status": "archived"})

    @action(detail=True, methods=["post"], url_path="add-comment")
    def add_comment(self, request: Request, pk=None) -> Response:
        post = self.get_object()
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required to comment."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD for comments — staff can approve."""

    queryset = Comment.objects.select_related("author", "post").all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy", "approve"):
            return [permissions.IsAdminUser()]
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def approve(self, request: Request, pk=None) -> Response:
        comment = self.get_object()
        comment.approved = True
        comment.save(update_fields=["approved"])
        return Response({"status": "approved"})
