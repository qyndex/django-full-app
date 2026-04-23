"""Class-based views for the HTML frontend of the full app."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PostForm
from .models import Article, Category, Comment, Post, Tag


class ArticleListView(ListView):
    """Public article list — published articles only."""

    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        qs = Article.objects.filter(
            status=Article.STATUS_PUBLISHED
        ).select_related("author", "category").prefetch_related("tags")
        q = self.request.GET.get("q", "")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q))
        tag_slug = self.kwargs.get("tag_slug")
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tags"] = Tag.objects.all()
        ctx["categories"] = Category.objects.all()
        ctx["query"] = self.request.GET.get("q", "")
        ctx["current_tag"] = self.kwargs.get("tag_slug", "")
        ctx["current_category"] = self.kwargs.get("category_slug", "")
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
        ).select_related("author", "category").prefetch_related("tags")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Article.objects.filter(pk=obj.pk).update(views=obj.views + 1)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["comments"] = self.object.comments.filter(approved=True).select_related("author")
        ctx["comment_form"] = CommentForm()
        return ctx

    def post(self, request, *args, **kwargs):
        """Handle comment submission on detail page."""
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            messages.success(request, "Your comment has been submitted and is awaiting approval.")
            return redirect("article-detail", slug=self.object.slug)
        ctx = self.get_context_data()
        ctx["comment_form"] = form
        return self.render_to_response(ctx)


class PostCreateView(LoginRequiredMixin, CreateView):
    """Create a new blog post."""

    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.status == Post.STATUS_PUBLISHED and not form.instance.published_at:
            form.instance.published_at = timezone.now()
        messages.success(self.request, "Post created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("article-detail", kwargs={"slug": self.object.slug})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing blog post — only author or staff."""

    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def get_queryset(self):
        qs = Post.objects.all()
        if not self.request.user.is_staff:
            qs = qs.filter(author=self.request.user)
        return qs

    def form_valid(self, form):
        if form.instance.status == Post.STATUS_PUBLISHED and not form.instance.published_at:
            form.instance.published_at = timezone.now()
        messages.success(self.request, "Post updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("article-detail", kwargs={"slug": self.object.slug})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a blog post — only author or staff."""

    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("dashboard")

    def get_queryset(self):
        qs = Post.objects.all()
        if not self.request.user.is_staff:
            qs = qs.filter(author=self.request.user)
        return qs

    def form_valid(self, form):
        messages.success(self.request, "Post deleted successfully.")
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, ListView):
    """Staff dashboard showing all articles."""

    model = Article
    template_name = "blog/dashboard.html"
    context_object_name = "articles"
    paginate_by = 20

    def get_queryset(self):
        qs = Article.objects.select_related("author", "category").prefetch_related("tags")
        if not self.request.user.is_staff:
            qs = qs.filter(author=self.request.user)
        return qs.order_by("-created_at")
