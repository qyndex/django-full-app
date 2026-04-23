"""Forms for creating and editing blog posts and comments."""
from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Form for creating and editing blog posts."""

    class Meta:
        model = Post
        fields = ["title", "content", "excerpt", "status", "category", "tags", "featured_image"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Post title"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 12}),
            "excerpt": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Brief summary (optional)"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.CheckboxSelectMultiple(),
        }


class CommentForm(forms.ModelForm):
    """Form for adding a comment to a blog post."""

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Write your comment...",
                }
            ),
        }
        labels = {
            "content": "Your comment",
        }
