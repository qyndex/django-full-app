"""Tests for blog HTML views — ArticleListView, ArticleDetailView, DashboardView."""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from apps.blog.models import Post
from apps.blog.tests.factories import PostFactory, PublishedPostFactory, TagFactory

User = get_user_model()


@pytest.mark.django_db
class TestArticleListView:
    """Tests for the article list — published posts only, supports ?q and tag filtering."""

    def test_list_loads(self, client: Client):
        url = reverse("article-list")
        response = client.get(url)
        assert response.status_code == 200

    def test_only_published_posts_shown(self, client: Client):
        published = PublishedPostFactory(title="Visible Post")
        PostFactory(title="Hidden Draft", status=Post.STATUS_DRAFT)
        url = reverse("article-list")
        response = client.get(url)
        assert response.status_code == 200
        assert "Visible Post" in response.content.decode()
        assert "Hidden Draft" not in response.content.decode()

    def test_search_filters_by_title(self, client: Client):
        PublishedPostFactory(title="Django Testing Guide")
        PublishedPostFactory(title="Unrelated Post")
        url = reverse("article-list") + "?q=Django+Testing"
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Django Testing Guide" in content
        assert "Unrelated Post" not in content

    def test_tag_filter(self, client: Client):
        tag = TagFactory(name="pytest")
        tagged_post = PublishedPostFactory(title="Post with pytest tag")
        tagged_post.tags.add(tag)
        untagged = PublishedPostFactory(title="Post without tag")
        url = reverse("articles-by-tag", kwargs={"tag_slug": tag.slug})
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Post with pytest tag" in content
        assert "Post without tag" not in content


@pytest.mark.django_db
class TestArticleDetailView:
    """Tests for the article detail view — published only, increments view count."""

    def test_detail_loads_for_published_post(self, client: Client):
        post = PublishedPostFactory(title="My Published Article")
        url = reverse("article-detail", kwargs={"slug": post.slug})
        response = client.get(url)
        assert response.status_code == 200
        assert "My Published Article" in response.content.decode()

    def test_draft_post_returns_404(self, client: Client):
        draft = PostFactory(title="Secret Draft", status=Post.STATUS_DRAFT)
        url = reverse("article-detail", kwargs={"slug": draft.slug})
        response = client.get(url)
        assert response.status_code == 404

    def test_view_count_increments_on_visit(self, client: Client):
        post = PublishedPostFactory()
        initial_views = post.views
        url = reverse("article-detail", kwargs={"slug": post.slug})
        client.get(url)
        post.refresh_from_db()
        assert post.views == initial_views + 1


@pytest.mark.django_db
class TestDashboardView:
    """Tests for the staff dashboard — requires login."""

    def test_dashboard_requires_login(self, client: Client):
        url = reverse("dashboard")
        response = client.get(url)
        # Should redirect to login
        assert response.status_code == 302
        assert "login" in response["Location"]

    def test_dashboard_loads_for_authenticated_user(self, client: Client):
        user = User.objects.create_user(
            username="dashuser", email="dash@example.com", password="pass123"
        )
        client.force_login(user)
        url = reverse("dashboard")
        response = client.get(url)
        assert response.status_code == 200

    def test_dashboard_shows_all_statuses(self, client: Client):
        """Dashboard shows draft and published (unlike public list)."""
        user = User.objects.create_user(
            username="staffuser", email="staff@example.com", password="pass123"
        )
        PostFactory(title="Draft Post", status=Post.STATUS_DRAFT)
        PublishedPostFactory(title="Published Post")
        client.force_login(user)
        url = reverse("dashboard")
        response = client.get(url)
        content = response.content.decode()
        assert "Draft Post" in content
        assert "Published Post" in content
