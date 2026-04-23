"""User profile model — one-to-one extension of Django's auth.User."""
from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Extended profile for every registered user."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
