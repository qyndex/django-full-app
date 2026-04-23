"""Tests for blog DRF API — ArticleViewSet, TagViewSet, CommentViewSet."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.blog.models import Post
from apps.blog.tests.factories import (
    CategoryFactory,
    CommentFactory,
    PostFactory,
    PublishedPostFactory,
    TagFactory,
)

User = get_user_model()

# Router registers at /api/blog/... but root urls mounts blog.urls at /api/
# Tags: /api/tags/, Articles: /api/articles/, Comments: /api/comments/
TAGS_URL = "/api/tags/"
ARTICLES_URL = "/api/articles/"
COMMENTS_URL = "/api/comments/"


@pytest.mark.django_db
class TestTagAPI:
    def test_list_tags_unauthenticated(self):
        TagFactory(name="python")
        TagFactory(name="django")
        client = APIClient()
        response = client.get(TAGS_URL)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data or isinstance(data, list)

    def test_create_tag_requires_admin(self):
        client = APIClient()
        response = client.post(TAGS_URL, {"name": "newtag"}, format="json")
        assert response.status_code in [401, 403]

    def test_create_tag_as_admin(self):
        admin = User.objects.create_superuser(
            username="tagadmin", email="tagadmin@example.com", password="adminpass"
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        response = client.post(TAGS_URL, {"name": "newtag"}, format="json")
        assert response.status_code == 201
        assert response.json()["name"] == "newtag"


@pytest.mark.django_db
class TestArticleAPI:
    def test_list_articles_unauthenticated_shows_published_only(self):
        PublishedPostFactory(title="Visible")
        PostFactory(title="Hidden Draft", status=Post.STATUS_DRAFT)
        client = APIClient()
        response = client.get(ARTICLES_URL)
        assert response.status_code == 200
        data = response.json()
        results = data.get("results", data)
        titles = [r["title"] for r in results]
        assert "Visible" in titles
        assert "Hidden Draft" not in titles

    def test_list_articles_staff_sees_all(self):
        admin = User.objects.create_superuser(
            username="listadmin", email="listadmin@example.com", password="adminpass"
        )
        PublishedPostFactory(title="Published")
        PostFactory(title="Draft", status=Post.STATUS_DRAFT)
        client = APIClient()
        client.force_authenticate(user=admin)
        response = client.get(ARTICLES_URL)
        assert response.status_code == 200
        data = response.json()
        results = data.get("results", data)
        titles = [r["title"] for r in results]
        assert "Published" in titles
        assert "Draft" in titles

    def test_retrieve_published_article(self):
        post = PublishedPostFactory(title="Detail Test")
        client = APIClient()
        response = client.get(f"{ARTICLES_URL}{post.pk}/")
        assert response.status_code == 200
        assert response.json()["title"] == "Detail Test"

    def test_create_article_requires_admin(self):
        client = APIClient()
        response = client.post(
            ARTICLES_URL,
            {"title": "New Post", "content": "Content here."},
            format="json",
        )
        assert response.status_code in [401, 403]

    def test_create_article_as_admin(self):
        admin = User.objects.create_superuser(
            username="createadmin", email="createadmin@example.com", password="adminpass"
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        response = client.post(
            ARTICLES_URL,
            {"title": "Admin Article", "content": "Body text."},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Admin Article"

    def test_publish_action_as_admin(self):
        admin = User.objects.create_superuser(
            username="publishadmin", email="publishadmin@example.com", password="adminpass"
        )
        post = PostFactory(status=Post.STATUS_DRAFT, author=admin)
        client = APIClient()
        client.force_authenticate(user=admin)
        response = client.post(f"{ARTICLES_URL}{post.pk}/publish/")
        assert response.status_code == 200
        assert response.json()["status"] == "published"
        post.refresh_from_db()
        assert post.status == Post.STATUS_PUBLISHED

    def test_filter_by_category(self):
        cat = CategoryFactory(name="Tech")
        PublishedPostFactory(title="Tech Post", category=cat)
        PublishedPostFactory(title="Other Post")
        client = APIClient()
        response = client.get(f"{ARTICLES_URL}?category={cat.slug}")
        assert response.status_code == 200
        data = response.json()
        results = data.get("results", data)
        titles = [r["title"] for r in results]
        assert "Tech Post" in titles
        assert "Other Post" not in titles

    def test_search_filter(self):
        PublishedPostFactory(title="Unique Search Term Post")
        PublishedPostFactory(title="Different Post")
        client = APIClient()
        response = client.get(f"{ARTICLES_URL}?search=Unique+Search+Term")
        assert response.status_code == 200
        data = response.json()
        results = data.get("results", data)
        assert len(results) >= 1
        assert any("Unique Search Term" in r["title"] for r in results)


@pytest.mark.django_db
class TestCommentAPI:
    def test_list_comments_unauthenticated(self):
        CommentFactory(approved=True)
        client = APIClient()
        response = client.get(COMMENTS_URL)
        assert response.status_code == 200

    def test_create_comment_requires_authentication(self):
        post = PublishedPostFactory()
        client = APIClient()
        response = client.post(
            COMMENTS_URL,
            {"post": post.pk, "content": "A comment."},
            format="json",
        )
        assert response.status_code in [401, 403]

    def test_create_comment_as_authenticated_user(self):
        user = User.objects.create_user(
            username="commenter", email="commenter@example.com", password="pass123"
        )
        post = PublishedPostFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            COMMENTS_URL,
            {"post": post.pk, "content": "Great article!"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["content"] == "Great article!"
        # New comments default to not approved
        assert response.json()["approved"] is False

    def test_approve_comment_requires_admin(self):
        user = User.objects.create_user(
            username="normaluser2", email="normal2@example.com", password="pass123"
        )
        comment = CommentFactory(approved=False)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(f"{COMMENTS_URL}{comment.pk}/approve/")
        assert response.status_code in [401, 403]

    def test_approve_comment_as_admin(self):
        admin = User.objects.create_superuser(
            username="approveadmin", email="approveadmin@example.com", password="adminpass"
        )
        comment = CommentFactory(approved=False)
        client = APIClient()
        client.force_authenticate(user=admin)
        response = client.post(f"{COMMENTS_URL}{comment.pk}/approve/")
        assert response.status_code == 200
        assert response.json()["status"] == "approved"
        comment.refresh_from_db()
        assert comment.approved is True


@pytest.mark.django_db
class TestAddCommentAction:
    """Tests for the add-comment action on ArticleViewSet."""

    def test_add_comment_via_article_action(self):
        user = User.objects.create_user(
            username="articlecommenter", email="ac@example.com", password="pass123"
        )
        post = PublishedPostFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            f"{ARTICLES_URL}{post.pk}/add-comment/",
            {"content": "Via article endpoint."},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["content"] == "Via article endpoint."

    def test_add_comment_unauthenticated_returns_401(self):
        post = PublishedPostFactory()
        client = APIClient()
        response = client.post(
            f"{ARTICLES_URL}{post.pk}/add-comment/",
            {"content": "Anonymous comment."},
            format="json",
        )
        assert response.status_code == 401
