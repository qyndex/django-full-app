"""Admin for the accounts app."""
from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "website", "created_at"]
    search_fields = ["user__username", "user__email", "bio"]
    readonly_fields = ["created_at"]
