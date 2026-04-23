"""Tests for blog models — Category, Tag, Post (Article alias), Comment."""
import pytest
from django.contrib.auth import get_user_model

from apps.blog.models import Article, Category, Comment, Post, Tag
from apps.blog.tests.factories import (
    CategoryFactory,
    CommentFactory,
    PostFactory,
    PublishedPostFactory,
    TagFactory,
)

User = get_user_model()


@pytest.mark.django_db
class TestCategoryModel:
    def test_create_category(self):
        cat = CategoryFactory(name="Tech News")
        assert cat.name == "Tech News"
        assert cat.slug == "tech-news"

    def test_slug_auto_generated(self):
        cat = CategoryFactory(name="My Cool Category")
        assert cat.slug == "my-cool-category"

    def test_str(self):
        cat = CategoryFactory(name="Django")
        assert str(cat) == "Django"

    def test_ordering_by_name(self):
        CategoryFactory(name="Zebra")
        CategoryFactory(name="Apple")
        names = list(Category.objects.values_list("name", flat=True))
        assert names == sorted(names)


@pytest.mark.django_db
class TestTagModel:
    def test_create_tag(self):
        tag = TagFactory(name="python")
        assert tag.name == "python"
        assert tag.slug == "python"

    def test_str(self):
        tag = TagFactory(name="django")
        assert str(tag) == "django"

    def test_slug_auto_generated_from_name(self):
        tag = TagFactory(name="Hello World")
        assert tag.slug == "hello-world"


@pytest.mark.django_db
class TestPostModel:
    def test_create_draft_post(self):
        post = PostFactory()
        assert post.status == Post.STATUS_DRAFT
        assert post.pk is not None

    def test_slug_auto_generated(self):
        post = PostFactory(title="My First Blog Post")
        assert post.slug == "my-first-blog-post"

    def test_slug_deduplication(self):
        post1 = PostFactory(title="Duplicate Title")
        post2 = PostFactory(title="Duplicate Title")
        assert post1.slug != post2.slug
        assert post2.slug.startswith("duplicate-title-")

    def test_str(self):
        post = PostFactory(title="Hello Post")
        assert str(post) == "Hello Post"

    def test_body_property_is_alias_for_content(self):
        post = PostFactory(content="The article body text.")
        assert post.body == "The article body text."

    def test_article_alias(self):
        """Article is an alias for Post for backward compatibility."""
        assert Article is Post

    def test_post_with_tags(self):
        tag1 = TagFactory(name="python")
        tag2 = TagFactory(name="django")
        post = PostFactory()
        post.tags.set([tag1, tag2])
        assert post.tags.count() == 2

    def test_post_with_category(self):
        cat = CategoryFactory(name="Web Dev")
        post = PostFactory(category=cat)
        assert post.category == cat
        assert post in cat.posts.all()

    def test_published_post_status(self):
        post = PublishedPostFactory()
        assert post.status == Post.STATUS_PUBLISHED
        assert post.published_at is not None

    def test_default_ordering_is_newest_first(self):
        post1 = PostFactory(title="First")
        post2 = PostFactory(title="Second")
        posts = list(Post.objects.all())
        # Newest should come first due to Meta.ordering = ["-created_at"]
        assert posts[0].pk == post2.pk
        assert posts[1].pk == post1.pk


@pytest.mark.django_db
class TestCommentModel:
    def test_create_comment(self):
        comment = CommentFactory()
        assert comment.pk is not None
        assert comment.approved is False

    def test_str(self):
        comment = CommentFactory()
        expected = f"Comment by {comment.author.username} on {comment.post.title}"
        assert str(comment) == expected

    def test_approve_comment(self):
        comment = CommentFactory(approved=False)
        comment.approved = True
        comment.save()
        refreshed = Comment.objects.get(pk=comment.pk)
        assert refreshed.approved is True

    def test_comment_fk_cascade_delete(self):
        comment = CommentFactory()
        post_pk = comment.post.pk
        comment.post.delete()
        assert not Comment.objects.filter(pk=comment.pk).exists()
