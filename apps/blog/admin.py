"""Admin registrations for the full app."""
from django.contrib import admin

from .models import Article, Comment, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ["author", "body", "is_approved", "created_at"]
    readonly_fields = ["author", "created_at"]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "status", "views", "published_at", "created_at"]
    list_filter = ["status", "tags"]
    search_fields = ["title", "body"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["tags"]
    inlines = [CommentInline]
    ordering = ["-created_at"]
    readonly_fields = ["views", "created_at", "updated_at"]

    actions = ["publish_articles", "archive_articles"]

    @admin.action(description="Publish selected articles")
    def publish_articles(self, request, queryset):
        import django.utils.timezone as tz
        queryset.update(status=Article.STATUS_PUBLISHED, published_at=tz.now())

    @admin.action(description="Archive selected articles")
    def archive_articles(self, request, queryset):
        queryset.update(status=Article.STATUS_ARCHIVED)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["article", "author", "is_approved", "created_at"]
    list_filter = ["is_approved"]
    search_fields = ["body", "author__username"]
    list_editable = ["is_approved"]
    ordering = ["-created_at"]
    actions = ["approve_comments"]

    @admin.action(description="Approve selected comments")
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
