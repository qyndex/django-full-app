"""Tests for accounts models — User and Profile."""
import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import Profile

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        assert user.is_staff
        assert user.is_superuser


@pytest.mark.django_db
class TestProfileModel:
    def test_profile_created_via_signal(self):
        """Signal creates a Profile automatically when a User is created."""
        user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="pass123",
        )
        assert hasattr(user, "profile")
        assert isinstance(user.profile, Profile)

    def test_profile_str(self):
        user = User.objects.create_user(
            username="struser",
            email="str@example.com",
            password="pass123",
        )
        assert str(user.profile) == f"Profile of {user.username}"

    def test_profile_defaults(self):
        user = User.objects.create_user(
            username="defaultuser",
            email="default@example.com",
            password="pass123",
        )
        profile = user.profile
        assert profile.bio == ""
        assert profile.website == ""
        assert not profile.avatar

    def test_profile_update(self):
        user = User.objects.create_user(
            username="updateuser",
            email="update@example.com",
            password="pass123",
        )
        user.profile.bio = "Hello, world!"
        user.profile.website = "https://example.com"
        user.profile.save()

        refreshed = Profile.objects.get(user=user)
        assert refreshed.bio == "Hello, world!"
        assert refreshed.website == "https://example.com"
