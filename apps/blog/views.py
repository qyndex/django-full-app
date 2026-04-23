"""Class-based views for the HTML frontend of the full app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import Article, Tag


class ArticleListView(ListView):
    """Public article list — published articles only."""

    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        qs = Article.objects.filter(
            status=Article.STATUS_PUBLISHED
        ).select_related("author").prefetch_related("tags")
        q = self.request.GET.get("q", "")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q))
        tag_slug = self.kwargs.get("tag_slug")
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tags"] = Tag.objects.all()
        ctx["query"] = self.request.GET.get("q", "")
        return ctx


class ArticleDetailView(DetailView):
    """Article detail page with approved comments."""

    model = Article
    template_name = "blog/article_detail.html"
    context_object_name = "article"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Article.objects.filter(
            status=Article.STATUS_PUBLISHED
        ).select_related("author").prefetch_related("tags")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Article.objects.filter(pk=obj.pk).update(views=obj.views + 1)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["comments"] = self.object.comments.filter(is_approved=True)
        return ctx


class DashboardView(LoginRequiredMixin, ListView):
    """Staff dashboard showing all articles."""

    model = Article
    template_name = "blog/dashboard.html"
    context_object_name = "articles"
    paginate_by = 20

    def get_queryset(self):
        return Article.objects.select_related("author").prefetch_related("tags").order_by("-created_at")
