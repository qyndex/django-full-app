"""DRF serializers for the full app API."""
from rest_framework import serializers

from .models import Article, Comment, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag."""

    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "slug"]


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment."""

    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "author_name", "body", "is_approved", "created_at"]
        read_only_fields = ["id", "author", "is_approved", "created_at"]


class ArticleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for article list view."""

    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    tag_names = serializers.StringRelatedField(source="tags", many=True, read_only=True)
    comment_count = serializers.IntegerField(
        source="comments.filter(is_approved=True).count",
        read_only=True,
        default=0,
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "author_name",
            "excerpt",
            "status",
            "tag_names",
            "views",
            "comment_count",
            "published_at",
            "created_at",
        ]
        read_only_fields = ["id", "slug", "views", "created_at"]


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Full serializer for article detail view."""

    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        source="tags",
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "author",
            "author_name",
            "body",
            "excerpt",
            "status",
            "tags",
            "tag_ids",
            "views",
            "comments",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "author", "views", "created_at", "updated_at"]
