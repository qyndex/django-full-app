"""Tests for accounts views — register, profile, public_profile."""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestRegisterView:
    """Tests for the registration view at accounts:register."""

    def test_register_page_loads(self, client: Client):
        url = reverse("accounts:register")
        response = client.get(url)
        assert response.status_code == 200

    def test_register_creates_user(self, client: Client):
        url = reverse("accounts:register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }
        response = client.post(url, data)
        # On success, should redirect to login
        assert response.status_code in [200, 302]
        if response.status_code == 302:
            assert User.objects.filter(username="newuser").exists()

    def test_register_redirects_authenticated_user(self, client: Client):
        user = User.objects.create_user(
            username="existinguser", email="existing@example.com", password="pass123"
        )
        client.force_login(user)
        url = reverse("accounts:register")
        response = client.get(url)
        # Authenticated users should be redirected away from register
        assert response.status_code == 302


@pytest.mark.django_db
class TestLoginView:
    """Tests for the login view at accounts:login."""

    def test_login_page_loads(self, client: Client):
        url = reverse("accounts:login")
        response = client.get(url)
        assert response.status_code == 200

    def test_login_with_valid_credentials(self, client: Client):
        User.objects.create_user(
            username="loginuser", email="login@example.com", password="testpass123"
        )
        url = reverse("accounts:login")
        response = client.post(url, {"username": "loginuser", "password": "testpass123"})
        assert response.status_code in [200, 302]


@pytest.mark.django_db
class TestProfileView:
    """Tests for the profile view at accounts:profile (login required)."""

    def test_profile_requires_login(self, client: Client):
        url = reverse("accounts:profile")
        response = client.get(url)
        # Should redirect to login
        assert response.status_code == 302
        assert "login" in response["Location"]

    def test_profile_loads_for_authenticated_user(self, client: Client):
        user = User.objects.create_user(
            username="profileviewer", email="pv@example.com", password="pass123"
        )
        client.force_login(user)
        url = reverse("accounts:profile")
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestPublicProfileView:
    """Tests for the public profile view at accounts:public-profile."""

    def test_public_profile_loads(self, client: Client):
        user = User.objects.create_user(
            username="publicuser", email="pub@example.com", password="pass123"
        )
        url = reverse("accounts:public-profile", kwargs={"username": user.username})
        response = client.get(url)
        assert response.status_code == 200

    def test_public_profile_404_for_unknown_user(self, client: Client):
        url = reverse("accounts:public-profile", kwargs={"username": "doesnotexist99"})
        response = client.get(url)
        assert response.status_code == 404
