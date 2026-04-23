"""DRF serializers for the blog API."""
from rest_framework import serializers

from .models import Category, Comment, Post, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag."""

    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "slug"]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category."""

    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "post_count"]
        read_only_fields = ["id", "slug"]

    def get_post_count(self, obj: Category) -> int:
        return obj.posts.filter(status=Post.STATUS_PUBLISHED).count()


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment.

    The ``post`` field is writable but not required so the serializer works
    both for the standalone ``/api/comments/`` endpoint (where the client
    sends ``post``) and for the nested ``/api/articles/{pk}/add-comment/``
    action (where the view injects the post via ``serializer.save(post=...)``)
    """

    author_name = serializers.CharField(source="author.username", read_only=True)
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), required=False,
    )

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "author_name", "content", "approved", "created_at"]
        read_only_fields = ["id", "author", "approved", "created_at"]


class PostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for post list view."""

    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    tag_names = serializers.StringRelatedField(source="tags", many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "author_name",
            "excerpt",
            "status",
            "category_name",
            "tag_names",
            "views",
            "comment_count",
            "published_at",
            "created_at",
        ]
        read_only_fields = ["id", "slug", "views", "created_at"]

    def get_comment_count(self, obj: Post) -> int:
        return obj.comments.filter(approved=True).count()


# Keep backward-compat alias
ArticleListSerializer = PostListSerializer


class PostDetailSerializer(serializers.ModelSerializer):
    """Full serializer for post detail view."""

    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
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
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "author",
            "author_name",
            "content",
            "excerpt",
            "status",
            "category",
            "category_id",
            "tags",
            "tag_ids",
            "featured_image",
            "views",
            "comments",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "author", "views", "created_at", "updated_at"]


# Keep backward-compat alias
ArticleDetailSerializer = PostDetailSerializer
